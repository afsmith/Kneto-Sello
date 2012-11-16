from celery.decorators import task
from reports import ReportGenerationService

@task(ignore_result=True)
def generate_reports():
    ReportGenerationService().generate_reports()

@task(ignore_result=True)
def generate_report(id):
    ReportGenerationService().generate_report(id)
    