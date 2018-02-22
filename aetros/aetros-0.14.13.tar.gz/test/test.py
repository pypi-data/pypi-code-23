import random
import aetros.backend
import time

job = aetros.backend.context()

loss = job.create_loss_channel()
acc = job.create_channel('accuracy', main=True, kpi=True)

epochs=3000
samples=10

job.epoch(total=epochs)

for i in range(0, epochs):
    job.epoch(epoch=i+1)
    print("hi" + str(i+1))
    loss.send(i, 25 + random.randint(-10, 20), 35 + random.randint(-10, 20))
    acc.send(i, 75 + random.randint(-25, 25))

    job.set_system_info('something', i)

    for j in range(0, samples):
        job.sample(j+1, samples)
        time.sleep(0.05)

print("Bye")