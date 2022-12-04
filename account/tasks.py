from celery import shared_task

@shared_task(bind = True)
def test_funciton(self):
    for i in range(10):
        print(i)
    return 'DONE'