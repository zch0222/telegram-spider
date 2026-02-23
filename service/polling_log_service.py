from dao.polling_log_dao import PollingLogDAO
from fastapi import Depends

class PollingLogService:
    def __init__(self, dao: PollingLogDAO = Depends()):
        self.dao = dao

    def search_logs(self, level=None, keyword=None, page=1, page_size=20):
        logs = self.dao.query_logs(level, keyword, page, page_size)
        total = self.dao.count_logs(level, keyword)
        
        # Convert datetime to string for JSON serialization
        for log in logs:
            if 'created_at' in log:
                log['created_at'] = str(log['created_at'])
                
        return {
            "list": logs,
            "total": total,
            "page": page,
            "page_size": page_size
        }
