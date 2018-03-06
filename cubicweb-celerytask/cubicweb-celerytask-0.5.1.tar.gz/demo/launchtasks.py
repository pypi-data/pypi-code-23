
from cubes.celerytask.entities import start_async_task

tasks = []
# a very simple task
tasks.append(start_async_task(cnx, 'hi_there', 'THERE', kw=42))

# a task showing several aspects of logging in cubicweb-celerytask
tasks.append(start_async_task(cnx, 'log'))

# a task with a progress bar
tasks.append(start_async_task(cnx, 'show-me-progress'))

cnx.commit()

print ("Started tasks:")
print ('\n'.join('  %s'%t.cwuri for t in tasks))
