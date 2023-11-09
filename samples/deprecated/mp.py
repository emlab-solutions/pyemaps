import multiprocessing as mp    

# processArray(): a parallel function that process an array based on start and 
#   end index positions.
def processArray(procId, array, indexes):
    startIdx, endIdx = indexes
    print("  Process #" + str(procId) + " startIdx=" + str(startIdx), " endIdx=" + str(endIdx))

    # Do some work:
    for i in range(startIdx, endIdx):
        print("    Process #" + str(procId) + " is computing index " + str(i), " with value " + str(array[i-startIdx]))


# jobDiv(): performs a simple job division between available CPU cores
def jobDiv(inputArray, numCPUs):
    jobs = []
    arrayLength = len(inputArray)

    jobRange = int(arrayLength / numCPUs)
    extra = arrayLength - (jobRange * numCPUs)

    prevEnd = 0
    for c in range(numCPUs):
        endIdx = (c * jobRange) + jobRange - 1
        if (c == (numCPUs-1)):
            endIdx += extra

        startIdx = prevEnd
        if ( (c > 0) and (startIdx+1 < arrayLength) ):
            startIdx += 1

        jobs.append( (startIdx, endIdx) )
        prevEnd = endIdx

    return jobs


if __name__ == '__main__':
    # Initialize dataset for multiprocessing with 50 numbers, with values from 80 to 131
    nums = range(80, 131)

    # How many CPU cores can be used for this dataset
    numCPUs = mp.cpu_count()
    if (numCPUs > len(nums)):
        numCPUs = len(nums)

    # This function returns a list of tuples containing array indexes for
    # each process to work on. When nums has 100 elements and numCPUs is 8,
    # it returns the following list:
    #   (0, 11), (12, 23), (24, 35), (36, 47), (48, 59), (60, 71), (72, 83), (84, 99)
    indexes = jobDiv(nums, numCPUs)

    # Prepare parameters for every process in the pool, where each process gets one tuple of:
    #   (cpu_id, array, array_indexes)
    jobArgs = []
    for id, arg in enumerate(indexes):
        start, end = arg
        print("Process #" + str(id) + " will work on indexes [" + str(start) + ":" + str(end) +
              "] with values: " + str(nums[start]) + " - " + str(nums[end]))
        jobArgs.append( (id, nums[start:end], arg) )

    print("* Starting Pool")

    # For every process, send the data for processing along with it's respective tuple of parameters
    print(f'Job args: {jobArgs}')
    with mp.Pool(processes=numCPUs) as p:
        sums = p.starmap(processArray, jobArgs)

    print("* Finished")

# from multiprocessing import Pool

# def f(x):
#     return x*x

# if __name__ == '__main__':
#     with Pool(5) as p:
#         print(p.imap(f, [1, 2, 3,4,5,6,7,8,9]))
    