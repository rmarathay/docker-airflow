from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
import psycopg2

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2018, 12, 17),
    "email": ["rmarathay@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
}

dag = DAG("scan",
        default_args=default_args,
        schedule_interval="@daily"
    )

t0 = BashOperator(
    task_id="root_node",
    bash_command="ls",
    run_as_user="airflow",
    dag=dag
    )

t2 = BashOperator(
    task_id="populate_nmap_results",
    bash_command="python3 /usr/local/pipeline-variant/scan/populate_nmap_results.py",
    run_as_user="airflow",
    dag=dag
)

default_params = {'node' : 0}
node_list = []
for node_id in range(1,17):
    params = default_params
    params['node'] = node_id
    t1 = BashOperator(
        task_id="nmap_scan_node_" + str(node_id),
        bash_command="python3 /usr/local/pipeline-variant/scan/nmap_scan.py {{ params.node }} ",
        run_as_user="airflow",
        params = params,
        dag=dag
        )
    if(len(node_list) == 0):
        t1.set_upstream(t0)
    else:
        t1.set_upstream(node_list[-1])
    node_list.append(t1)
t2.set_upstream(node_list[-1])