import yt_dlp
import os
import asyncio
import json
import time
from dao.yt_dlp_dao import YtDlpDAO
from fastapi import Depends
from db import get_db
from core import get_redis
import aioredis
from core.config import MEDIA_DOWNLOAD_SAVE_PATH

# Redis Key Prefix
YT_DLP_PROGRESS_PREFIX = "yt_dlp:progress:"

class YtDlpService:
    def __init__(self, dao: YtDlpDAO = Depends(), redis: aioredis.Redis = Depends(get_redis)):
        self.dao = dao
        self.redis = redis

    async def submit_task(self, url: str):
        # Create task in DB
        task_id = self.dao.create_task(url)
        
        # Start download in background
        asyncio.create_task(self.download_video(task_id, url))
        
        return task_id

    async def download_video(self, task_id: int, url: str):
        # We need a new DB session for the background task since the injected one is closed after request
        # But here we are using the injected DAO which uses injected DB.
        # This is problematic for background tasks in FastAPI.
        # So we should create a new DAO instance with a new DB connection.
        
        # Manually create DB connection
        from db.session import Database
        db_conn = Database().get_conn()
        dao = YtDlpDAO(db_conn)
        
        try:
            dao.update_task_status(task_id, "downloading")
            
            # Prepare download options
            download_dir = os.path.join(MEDIA_DOWNLOAD_SAVE_PATH, 'yt_dlp')
            os.makedirs(download_dir, exist_ok=True)
            output_template = os.path.join(download_dir, '%(title)s.%(ext)s')
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                        downloaded_bytes = d.get('downloaded_bytes', 0)
                        
                        progress = 0
                        if total_bytes > 0:
                            progress = (downloaded_bytes / total_bytes) * 100
                            
                        speed = d.get('speed', 0)
                        if speed:
                            speed_str = f"{speed / 1024 / 1024:.2f} MiB/s"
                        else:
                            speed_str = "N/A"
                            
                        eta = d.get('eta', 0)
                        eta_str = str(eta) if eta else "N/A"
                        
                        # Update DB
                        # We use sync DB connection so it's fine in this hook
                        dao.update_task_progress(task_id, round(progress, 2), speed_str, eta_str, downloaded_bytes, total_bytes)
                        
                    except Exception as e:
                        print(f"Error in progress hook: {e}")

            ydl_opts = {
                'outtmpl': output_template,
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
                'retries': 3,            # Limit retries
                'fragment_retries': 3,   # Limit fragment retries
                'skip_unavailable_fragments': True, # Skip bad fragments
                'ignoreerrors': True,    # Continue on error (though we handle exception)
                # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' # Optional: force mp4
            }
            
            # Run blocking yt-dlp in executor
            loop = asyncio.get_running_loop()
            info = await loop.run_in_executor(None, lambda: self._run_yt_dlp(url, ydl_opts))
            
            filename = info.get('_filename', 'unknown')
            title = info.get('title', 'unknown')
            
            dao.complete_task(task_id, title, filename)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Task {task_id} failed: {error_msg}")
            dao.fail_task(task_id, error_msg)
        finally:
            # Ensure connection is closed
            try:
                db_conn.close()
            except:
                pass

    def _run_yt_dlp(self, url, opts):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Add filename to info manually because prepare_filename might differ slightly if postprocessors run
                # But usually it's correct.
                info['_filename'] = ydl.prepare_filename(info)
                return info
        except KeyboardInterrupt:
            # Re-raise to let the main loop handle it, but executor might swallow it?
            raise
        except Exception as e:
            # If ignoreerrors is True, info might be None if download failed completely
            # We should check this.
            raise e

    async def get_all_tasks(self):
        return self.dao.get_all_tasks()
        
    async def get_task_progress_stream(self):
        """
        Generator for SSE. 
        Since we update DB in real-time (mostly), we can poll DB.
        """
        while True:
            # Use a fresh connection for polling to avoid stale data if connection is reused poorly
            # Or rely on short-lived connections in DAO if using pool.
            # But self.dao uses injected DB which is request-scoped. 
            # This generator runs for a long time. 
            # So we need to manage DB connection inside the loop or use a persistent one?
            # Creating a new connection every second is expensive.
            # Ideally we should use a connection from pool and release it.
            # But our Database class creates a new connection each time.
            # Let's create one connection for this stream.
            
            from db.session import Database
            db_conn = Database().get_conn()
            dao = YtDlpDAO(db_conn)
            
            try:
                tasks = dao.get_all_tasks()
                
                # Format tasks
                formatted_tasks = []
                for task in tasks:
                    task_copy = task.copy()
                    if 'created_at' in task_copy:
                        task_copy['created_at'] = str(task_copy['created_at'])
                    if 'updated_at' in task_copy:
                        task_copy['updated_at'] = str(task_copy['updated_at'])
                    if 'progress' in task_copy:
                        task_copy['progress'] = float(task_copy['progress'])
                    formatted_tasks.append(task_copy)
                
                yield f"data: {json.dumps(formatted_tasks)}\n\n"
                
            except Exception as e:
                print(f"Error in SSE stream: {e}")
                # Wait a bit before retry
                await asyncio.sleep(5)
            finally:
                # Close connection after each query? No, keep it open?
                # If we keep it open, we might face timeouts.
                # Let's close it to be safe and simple, although inefficient.
                # Or better: create it once outside loop.
                # But if MySQL server closes it, we crash.
                # Let's close it every time for robustness given simple setup.
                try:
                    db_conn.close()
                except:
                    pass
            
            await asyncio.sleep(1)
