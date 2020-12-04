# Guillaume Cadorette - cadg3202 - 17 040 202

import time

DATA_FILE_PATH = "data/u.item"
USER_FILE_PATH = "data/u.user"
BASE_FILE_PATH = "data/u_.base"
TEST_FILE_PATH = "data/u_.test"
EPSILON = 0.2  # seuil de convergence


class Rating:
    def __init__(self, user, film, rating):
        self.user = int(user)
        self.film = int(film)
        self.rating = int(rating)


def kmeans(amtOfClusters, values, usersInFile, filmsInFile, usersMap):
    clusters = []
    clustersMid = []
    for ind in range(amtOfClusters):
        clustersMid.append(usersInFile[50 * ind])
        clusters.append([usersInFile[50 * ind]])
    midValues = []
    for ind in range(amtOfClusters):
        midValues.append([x for x in values if x.user == clustersMid[ind]])
    changed = True
    amtOfIterations = 0
    while changed and amtOfIterations < 10:
        changed = False
        for user in usersInFile:
            minDiff = 2 ** 31
            chosenCluster = -1
            for clusterInd in range(amtOfClusters):
                if clustersMid[clusterInd] != user and user not in clustersMid:
                    diff = 0
                    ind = usersMap[user][0]
                    while ind < len(values) and values[ind].user == user:
                        midRatings = [x.rating for x in midValues[clusterInd] if x.film == values[ind].film]
                        for val in midRatings:
                            diff += abs(values[ind].rating - val) / len(midRatings)
                        ind += 1
                    if diff != 0.0:
                        diff = diff / len(midValues[clusterInd])
                        if diff < minDiff:
                            chosenCluster = clusterInd
                            minDiff = diff
            for cl in range(amtOfClusters):
                if user in clusters[cl]:
                    clusters[cl].remove(user)
                    break
            clusters[chosenCluster].append(user)
        amtChanged = 0
        for clusterInd in range(amtOfClusters):
            if len(clusters[clusterInd]) <= 1:
                continue
            prevMid = clustersMid[clusterInd]
            sumVal = 0
            amtMovies = 0
            for film in filmsInFile:
                atLeastOne = False
                for u in clusters[clusterInd]:
                    filmRatings = [x.rating for x in values[usersMap[u][0]: usersMap[u][1]] if x.film == film]
                    if filmRatings:
                        sumVal += sum(filmRatings) / len(filmRatings)
                        atLeastOne = True
                if atLeastOne:
                    amtMovies += 1

            avg = sumVal / amtMovies
            ratingsMid = [x.rating for x in midValues[clusterInd]]
            avgMid = sum(ratingsMid) / len(ratingsMid)
            closestMid = abs(avg - avgMid)
            bestMid = clustersMid[clusterInd]
            mins = []
            for user in clusters[clusterInd]:
                filmRatings = [x.rating for x in values[usersMap[user][0]: usersMap[user][1]]]
                rating = sum(filmRatings) / len(filmRatings)
                dist = abs(avg - rating)
                if dist < closestMid and abs(dist - closestMid) > EPSILON:
                    mins.append(abs(dist - closestMid))
                    closestMid = dist
                    bestMid = user
                    amtChanged += 1
            if bestMid != prevMid:
                midValues[clusterInd] = [x for x in values[usersMap[bestMid][0]: usersMap[bestMid][1]]]
                clustersMid[clusterInd] = bestMid
                changed = True
                for cl in range(amtOfClusters):
                    if bestMid in clusters[cl]:
                        clusters[cl].remove(bestMid)
                clusters[clusterInd].append(bestMid)
        amtOfIterations += 1
    return clusters, clustersMid


if __name__ == "__main__":

    ratings = []
    for i in range(1, 6):
        with open(BASE_FILE_PATH.replace("_", str(i))) as f:
            ratings.append([])
            usersInFile = []
            filmsInFile = []
            usersMap = {}
            prevUser = -1
            lineNbr = 0
            user = 0
            for line in f:
                entry = line.split("\t")
                ratings[-1].append(Rating(entry[0], entry[1], entry[2]))
                user = int(entry[0])
                film = int(entry[1])
                if prevUser != user:
                    usersInFile.append(user)
                    prevUser = user
                    usersMap[user] = [lineNbr]
                    if user > 1:
                        usersMap[user - 1].append(lineNbr)
                if film not in filmsInFile:
                    filmsInFile.append(film)
                lineNbr += 1
            usersMap[user].append(lineNbr - 1)
        for k in range(2, 20):
            clusters, clustersMid = kmeans(k, ratings[-1], usersInFile, filmsInFile, usersMap)
            print("Finished clustering!")
            estimatedRatings = []
            with open(TEST_FILE_PATH.replace("_", str(i))) as f:
                beg = time.process_time()
                for line in f:
                    entry = line.replace("\n", "").split("\t")
                    trueRating = Rating(entry[0], entry[1], entry[2])
                    sumScore = 0
                    amtUsers = 0
                    clusterIndex = -1
                    for index, cl in enumerate(clusters):
                        if next((x for x in cl if x == trueRating.user), None):
                            clusterIndex = index
                    sumRatings = 0
                    amt = 0
                    for user, lines in usersMap.items():
                        if user in clusters[clusterIndex]:
                            for l in range(lines[0], lines[1]):
                                sumRatings += ratings[-1][l].rating
                                amt += 1
                    calculatedRatings = -1
                    if sumRatings > 0:
                        calculatedRatings = sumRatings / amt
                    estimatedRatings.append((trueRating.rating, calculatedRatings))
            print(time.process_time() - beg)
            removedClutter = [x for x in estimatedRatings if x[1] != -1]
            print("{} clusters pour le fichier {}: {} manquants sur 20000".format(k, i, len(estimatedRatings) - len(removedClutter)))
            avg = sum([abs(true - calculated) for true, calculated in removedClutter]) / len(removedClutter)
            variance = sum([(avg - abs(true - calculated)) ** 2 for true, calculated in removedClutter]) / (len(removedClutter) - 1)
            print("moyenne de {} et variance de {}\n".format(avg, variance))
            # traitement avec l'autre
    print("me:)")
