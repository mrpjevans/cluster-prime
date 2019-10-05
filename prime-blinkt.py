from mpi4py import MPI
import time
import sys
from blinkt import set_pixel, set_brightness, show, clear

# Define colours
colours = [
    [128, 128, 128],
    [0, 0, 128],
    [0, 0, 255],
    [0, 128, 0],
    [0, 255, 0],
    [128, 0, 0],
    [255, 0, 0],
    [128, 128, 0],
    [255, 255, 0],
    [255, 255, 255]
]

# Set Blinkt! brightness
set_brightness(0.1)

# Light the blinkt up based on the current value
def set_blinkt(val):
    clear()
    s_val = str(val)[::-1]
    i = 0
    while i < len(s_val):
        num = int(s_val[i])
        col = colours[num]
        set_pixel(i, col[0], col[1], col[2])
        i += 1
    show()

# Attach to the cluster and find out who I am and how big it is
comm = MPI.COMM_WORLD
my_rank = comm.Get_rank()
cluster_size = comm.Get_size()

# Number to start on, based on the node's rank
start_number = (my_rank * 2) + 1

# When to stop. Play around with this value!
end_number = int(sys.argv[1])

# Make a note of the start time
start = time.time()

# List of discovered primes for this node
primes = []

# Loop through the numbers using rank number to divide the work
for candidate_number in range(start_number,
                              end_number, cluster_size * 2):

    # Display the number on Blinkt!
    set_blinkt(candidate_number)

    # Assume this number is prime
    found_prime = True

    # Go through all previous numbers and see if any divide without remainder
    for div_number in range(2, candidate_number):
        if candidate_number % div_number == 0:
            found_prime = False
            break

    # If we get here, nothing divided, so it's a prime number
    if found_prime:
        # Uncomment the next line to see the primes as they are found (slower)
        # print('Node ' + str(my_rank) + ' found ' + str(candidate_number))
        primes.append(candidate_number)

# Once complete, send results to the governing node
results = comm.gather(primes, root=0)

# If I am the governing node, show the results
if my_rank == 0:

    # How long did it take?
    end = round(time.time() - start, 2)

    print('Find all primes up to: ' + str(end_number))
    print('Nodes: ' + str(cluster_size))
    print('Time elasped: ' + str(end) + ' seconds')

    # Each process returned an array, so lets merge them
    merged_primes = [item for sublist in results for item in sublist]
    merged_primes.sort()
    print('Primes discovered: ' + str(len(merged_primes)))
    # Uncomment the next line to see all the prime numbers
    # print(merged_primes)
