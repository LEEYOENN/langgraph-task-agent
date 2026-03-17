from sqlalchemy.orm import Session
from src.app.repository import TaskRepository
from src.app.agent import InvestmentAnalysisAgent

# 에이전트는 서비스 단에서 싱글톤 패턴처럼 한 번만 띄워서 사용합니다.
agent = InvestmentAnalysisAgent()
repo = TaskRepository()

class InvestmentAnalysisService:
    def run_analysis(self, db: Session, target_company: str, user_query: str):
        # 1. DB에 pending 상태로 작업 데이터 생성
        task = repo.create_task(db, target_name=target_company)

        try: 
            # 2. 작업 상태 업데이트
            repo.update_task(db, task.task_id, status="IN_PROGRESS")
            
            # 3. 투자 분석 에이전트 실행
            print(f"[{task.task_id}] 에이전트 실행 시작: {target_company}")
            final_report = agent.run(company_name=target_company, query=user_query)
            
            # 4. 성공 시 결과 저장
            updated_task = repo.update_task(db, task.task_id, status="COMPLETED", result_text=final_report)
            
            return {
                "task_id": updated_task.task_id,
                "target_company": updated_task.target_name,
                "status": updated_task.status,
                "result_text": updated_task.result_text
            }
        
        except Exception as e:
            # 5. 실패 시 에러 로깅
            print(f"[{task.task_id}] 에이전트 실행 중 에러 발생: {e}")
            updated_task = repo.update_task(db, task.task_id, status="ERROR", error=str(e))

            return {
                "task_id": updated_task.task_id,
                "target_company": updated_task.target_name,
                "status": updated_task.status,
                "result_text": "분석 중 오류가 발생했습니다."
            }