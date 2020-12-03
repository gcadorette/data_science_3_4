# Guillaume Cadorette - cadg3202 - 17 040 202

DATA_FILE_PATH = "data/u.item"
USER_FILE_PATH = "data/u.user"
BASE_FILE_PATH = "data/u_.base"
TEST_FILE_PATH = "data/u_.test"
EPSILON = 0.66  # seuil de convergence


class Rating:
    def __init__(self, user, film, rating):
        self.user = int(user)
        self.film = int(film)
        self.rating = int(rating)


"""
class Film:
    def __init__(self, year, genre):
        self.year = int(year)
        self.genre = genre


class User:
    def __init__(self, id, age, sex, job):
        self.id = int(id)
        self.age = int(age) // 25
        self.sex = 0 if sex == "M" else 1
        self.job = job
"""


def kmeans(amtOfClusters, values, usersInFile, filmsInFile):
    clusters = []
    clustersMid = []
    for ind in range(amtOfClusters):
        clustersMid.append(usersInFile[25*ind])
        clusters.append([usersInFile[25*ind]])
    midValues = []
    for ind in range(amtOfClusters):
        midValues.append([x for x in values if x.user == clustersMid[ind]])
    changed = True
    amtOfIterations = 0
    while changed:
        changed = False
        for user in usersInFile:
            minDiff = 2**31
            chosenCluster = -1
            for clusterInd in range(amtOfClusters):
                if clustersMid[clusterInd] != user and user not in clustersMid:
                    diff = 0
                    amt = 0
                    ind = 0
                    for j, x in enumerate(values):
                        if x.user == user:
                            ind = j
                            break
                    while ind < len(values) and values[ind].user == user:
                        midRatings = [x for x in midValues[clusterInd] if x.film == values[ind].film]
                        for val in midRatings:
                            diff += abs(values[ind].rating - val.rating) / len(midRatings)
                            amt += 1
                        ind += 1
                    if amt > 0:
                        #diff = diff / len(midValues[clusterInd])
                        if diff < minDiff:
                            chosenCluster = clusterInd
                            minDiff = diff
            for cl in range(amtOfClusters):
                if user in clusters[cl]:
                    clusters[cl].remove(user)
            clusters[chosenCluster].append(user)
        amtChanged = 0
        for clusterInd in range(amtOfClusters):
            prevMid = clustersMid[clusterInd]
            sumVal = 0
            amtMovies = 0
            for film in filmsInFile:
                filmRatings = [x.rating for x in values if x.film == film and x.user in clusters[clusterInd]]
                if filmRatings:
                    sumVal += sum(filmRatings) / len(filmRatings)
                    amtMovies += 1
                    pass
            avg = sumVal / amtMovies
            ratingsMid = [x.rating for x in values if x.user == clustersMid[clusterInd]]
            closestMid = abs(avg - sum(ratingsMid)) / len(ratingsMid)
            bestMid = clustersMid[clusterInd]
            mins = []
            for user in clusters[clusterInd]:
                filmRatings = [x.rating for x in values if x.user == user]
                rating = sum(filmRatings) / len(filmRatings)
                if abs(abs(avg - rating) - closestMid) > EPSILON:
                    mins.append(abs(abs(avg - rating) - closestMid))
                    closestMid = abs(avg - rating)
                    bestMid = user
                    amtChanged += 1
            if bestMid != prevMid:
                print("Cluster : {}".format(clusterInd))
                print(mins)
                midValues[clusterInd] = [x for x in values if x.user == clustersMid[clusterInd]]
                clustersMid[clusterInd] = bestMid
                changed = True
                for cl in range(amtOfClusters):
                    if bestMid in clusters[cl]:
                        clusters[cl].remove(bestMid)
                clusters[clusterInd].append(bestMid)
        print(amtOfIterations)
        amtOfIterations += 1
        print("lol")
    print("hihi")


if __name__ == "__main__":

    ratings = []
    for i in range(1, 6):
        usersInFile = []
        filmsInFile = []
        with open(BASE_FILE_PATH.replace("_", str(i))) as f:
            ratings.append([])
            for line in f:
                entry = line.split("\t")
                ratings[-1].append(Rating(entry[0], entry[1], entry[2]))
                if int(entry[0]) not in usersInFile:
                    usersInFile.append(int(entry[0]))
                if int(entry[1]) not in filmsInFile:
                    filmsInFile.append(int(entry[1]))
        for k in range(5, 9):
            kmeans(k, ratings[-1], usersInFile, filmsInFile)
    print("me:)")
