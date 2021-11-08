from datetime import timedelta  
import airflow  
from airflow import DAG  
from airflow.providers.amazon.aws.sensors.s3_prefix import S3PrefixSensor
from airflow.providers.amazon.aws.operators.emr_create_job_flow import EmrCreateJobFlowOperator
from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator 
from airflow.providers.amazon.aws.operators.emr_terminate_job_flow import EmrTerminateJobFlowOperator
from airflow.providers.amazon.aws.sensors.emr_step import EmrStepSensor

# Custom Operators deployed as Airflow plugins
from awsairflowlib.operators.aws_glue_job_operator import AWSGlueJobOperator
from awsairflowlib.operators.aws_glue_crawler_operator import AWSGlueCrawlerOperator
from awsairflowlib.operators.aws_copy_s3_to_redshift import CopyS3ToRedshiftOperator


S3_BUCKET_NAME = "lijianwe-airflow"  
  
default_args = {  
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
    'retries': 0,
    'retry_delay': timedelta(minutes=2),
    'provide_context': True,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

dag = DAG(  
    'Midea-demo',
    default_args=default_args,
    dagrun_timeout=timedelta(hours=2),
    schedule_interval='0 3 * * *'
)


execution_date = "{{ execution_date }}"  

S3_URI = "s3://{}/scripts/emr/".format("lijianwe-airflow")  
 
SPARK_STEPS = [
        {
            'Name': 'calculate_pi',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': ['/usr/lib/spark/bin/run-example', 'SparkPi', '10'],
            },
        }
    ]


step_adder = EmrAddStepsOperator(
    task_id='add_steps',
    job_flow_id="j-2DUW0MBX5TBEE",
    aws_conn_id='aws_default',
    steps=SPARK_STEPS,
    dag=dag
)


step_checker = EmrStepSensor(
    task_id='watch_step',
    job_flow_id="j-2DUW0MBX5TBEE",
    step_id="{{ task_instance.xcom_pull('add_steps', key='return_value')[0] }}",
    aws_conn_id='aws_default',
    dag=dag
)


step_adder >> step_checker






