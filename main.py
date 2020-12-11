# Guillaume Cadorette - cadg3202 - 17 040 202

import time

DATA_FILE_PATH = "data/u.item"
USER_FILE_PATH = "data/u.user"
BASE_FILE_PATH = "data/u_.base"
TEST_FILE_PATH = "data/u_.test"
EPSILON = 0.2  # seuil de convergence
FILENAME = "results" + str(time.time()) + ".csv"


class Rating:
    def __init__(self, user, film, rating):
        self.user = int(user)
        self.film = int(film)
        self.rating = int(rating)
        self.categoryRating = 0
        if 2 >= self.rating >= 0:
            self.categoryRating = 1
        elif self.rating == 3:
            self.categoryRating = 2
        else:
            self.categoryRating = 3


def initialiseClusters(amtOfClusters, values):
    clusters = []
    clustersMid = []
    for ind in range(amtOfClusters):
        clustersMid.append(usersInFile[50 * ind])
        clusters.append([usersInFile[50 * ind]])
    midValues = []
    for ind in range(amtOfClusters):
        midValues.append([x for x in values if x.user == clustersMid[ind]])
    return clusters, clustersMid, midValues


def getMode(modes):
    mode = -1
    modeVal = 2 ** 31
    for ind, m in enumerate(modes):
        if m < modeVal:
            modeVal = m
            mode = i
    return mode


def nearestNeighbors(values, usersInFile, usersMap):
    beg = time.process_time()
    entriesPerUsers = {}
    for user in usersInFile:
        entriesPerUsers[user] = [x for x in values[usersMap[user][0]: usersMap[user][1]]]
    nearestNeighbor = {}
    for user in usersInFile:
        entries = {}
        for otherUser in usersInFile:
            if otherUser != user:
                if otherUser not in nearestNeighbor.keys():
                    neighbors = []
                    for rating in entriesPerUsers[user]:
                        othersRating = None
                        for r in entriesPerUsers[otherUser]:
                            if r.film == rating.film:
                                othersRating = r
                                break
                        if othersRating:
                            neighbors.append(abs(othersRating.rating - rating.rating))
                    if neighbors:
                        entries[otherUser] = neighbors
                elif user in nearestNeighbor[otherUser].keys() and nearestNeighbor[otherUser][user] :
                    entries[otherUser] = nearestNeighbor[otherUser][user]
        nearestNeighbor[user] = entries
    print(time.process_time() - beg)
    return nearestNeighbor


def method3(amtOfClusters, values, usersInFile, filmsInFile, usersMap):
    print("method3 :)")
    weights = []
    clusters, clustersMid, midValues = initialiseClusters(amtOfClusters, values)
    # creer une matrice 2d de taille amtclusters * amtfilms
    for _ in range(amtOfClusters):
        filmWeights = {}
        for film in filmsInFile:
            filmWeights[film] = 1 / len(filmsInFile)
        weights.append(filmWeights)
    changed = True
    amtOfIterations = 0
    while changed:
        changed = False
        for user in usersInFile:
            minDist = 2 ** 31
            bestCl = -1
            userIndBeg = usersMap[user][0]
            for cl in range(amtOfClusters):
                distSum = 0
                if clustersMid[cl] != user and user not in clustersMid:
                    ind = usersMap[user][0]
                    while ind < len(values) and values[ind].user == user:
                        distSum += sum(
                            [weights[cl][x.film] * (values[ind].rating - x.rating) ** 2 for x in midValues[cl] if
                             x.film == values[ind].film])
                        ind += 1

                distSum = distSum ** (1 / 2)
                if distSum < minDist:
                    minDist = distSum
                    bestCL = cl

            for cl in range(amtOfClusters):
                if user in clusters[cl]:
                    clusters[cl].remove(user)
                    break
            clusters[bestCL].append(user)

        # change the weights
        weightsForAdjustements = []
        for cl in range(amtOfClusters):
            weightsForAdjustements.append({})
            for user in clusters[cl]:
                if user != clustersMid[cl]:
                    for i in range(usersMap[user][0], usersMap[user][1] + 1):
                        if values[i].film in weightsForAdjustements[cl].keys():
                            weightsForAdjustements[cl][values[i].film].append(values[i].rating)
                        else:
                            weightsForAdjustements[cl][values[i].film] = [values[i].rating]
        # normalize the weights
        sumPerCl = []
        amtPerCl = []
        avgPerCl = []
        for cl, weightsAdjustments in enumerate(weightsForAdjustements):
            sumPerCl.append(0)
            amtPerCl.append(0)
            for film, entries in weightsAdjustments.items():
                if entries:
                    avg = sum(entries) / len(entries)
                    variance = sum([(avg - entry) ** 2 for entry in entries]) / (len(entries))
                    weights[cl][film] = weights[cl][film] / (1 + variance)
                    sumPerCl[cl] += weights[cl][film] ** 2
                    amtPerCl[cl] += 1

        for cl in range(amtOfClusters):
            if amtPerCl[cl] == 0:
                amtPerCl[cl] = 1
            avgPerCl.append(sumPerCl[cl] / amtPerCl[cl])
            for film in filmsInFile:
                if sumPerCl[cl] == 0:
                    sumPerCl[cl] = 1
                weights[cl][film] = weights[cl][film] / (sumPerCl[cl] ** 1 / 2)

        for cl in range(amtOfClusters):
            prevMid = clustersMid[cl]
            midRatings = [x.rating * weights[cl][x.film] for x in midValues[cl]]
            midAvg = sum(midRatings) / len(midRatings)
            midDiff = abs(avgPerCl[cl] - midAvg)
            mid = clustersMid[cl]
            for user in clusters[cl]:
                if user != clustersMid[cl]:
                    userRatings = [x.rating * weights[cl][x.film] for x in values[usersMap[user][0]: usersMap[user][1]]]
                    userAvg = sum(userRatings) / len(userRatings)
                    diff = abs(avgPerCl[cl] - userAvg)
                    if diff < midDiff and abs(diff - midDiff) > EPSILON:
                        mid = user
                        midDiff = diff
            if mid != prevMid:
                midValues[cl] = [x for x in values[usersMap[mid][0]: usersMap[mid][1]]]
                clustersMid[cl] = mid
                changed = True
                for cl in range(amtOfClusters):
                    if mid in clusters[cl]:
                        clusters[cl].remove(mid)
                clusters[cl].append(mid)
        amtOfIterations += 1
    return clusters, clustersMid, weights


def kmode(amtOfClusters, values, usersInFile, filmsInFile, usersMap):
    clusters, clustersMid, midValues = initialiseClusters(amtOfClusters, values)
    changed = True
    amtOfIterations = 0
    while changed:
        changed = False
        for user in usersInFile:
            minDiff = 2 ** 31
            chosenCluster = -1
            for clusterInd in range(amtOfClusters):
                if clustersMid[clusterInd] != user and user not in clustersMid:
                    diff = 0
                    ind = usersMap[user][0]
                    while ind < len(values) and values[ind].user == user:
                        midRatings = [0 if values[ind].categoryRating == x.categoryRating else 1 for x in
                                      midValues[clusterInd] if
                                      x.film == values[ind].film]
                        if midRatings:
                            diff += sum(midRatings) / len(midRatings)
                        ind += 1
                    if 0 < diff < minDiff:
                        chosenCluster = clusterInd
                        minDiff = diff
            for cl in range(amtOfClusters):
                if user in clusters[cl]:
                    clusters[cl].remove(user)
                    break
            clusters[chosenCluster].append(user)
        amtOfChanged = 0
        for clusterInd in range(amtOfClusters):
            if len(clusters[clusterInd]) <= 1:
                continue
            prevMid = clustersMid[clusterInd]
            sumVal = 0
            amtMovies = 0
            modes = [0, 0, 0]
            for film in filmsInFile:
                atLeastOne = False
                for u in clusters[clusterInd]:
                    for x in values[usersMap[u][0]: usersMap[u][1]]:
                        if x.film == film:
                            modes[x.categoryRating - 1] += 1
                            atLeastOne = True
                if atLeastOne:
                    amtMovies += 1

            bestMid = clustersMid[clusterInd]
            modeVal = 2 ** 31
            mode = getMode(modes)

            ratingsMid = [0 if x.categoryRating == mode else 1 for x in midValues[clusterInd]]
            diffMid = sum(ratingsMid) / len(ratingsMid)
            for user in clusters[clusterInd]:
                if user != clustersMid[clusterInd]:
                    filmRatings = [0 if x.categoryRating == mode else 1 for x in
                                   values[usersMap[user][0]: usersMap[user][1]]]
                    dist = sum(filmRatings) / len(filmRatings)
                    if dist < diffMid and abs(dist - diffMid) > EPSILON:
                        diffMid = dist
                        bestMid = user
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


def kmeans(amtOfClusters, values, usersInFile, filmsInFile, usersMap):
    clusters, clustersMid, midValues = initialiseClusters(amtOfClusters, values)
    changed = True
    amtOfIterations = 0
    while changed and amtOfIterations < 10:
        changed = False
        # deplacement de mes usagers dans les clusters appropries
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
        # deplacement des centroides
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
    # with open(FILENAME, "w") as file:
    #   file.write("Cluster,Fichier,Manquants,Moyenne,Variance")
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
        k = 15
        """
        clusters3, clustersMid3, weights = method3(k, ratings[-1], usersInFile, filmsInFile, usersMap)
        clusters, clustersMid = kmeans(k, ratings[-1], usersInFile, filmsInFile, usersMap)
        clustersMod, clustersMidMod = kmode(k, ratings[-1], usersInFile, filmsInFile, usersMap)
        """
        neighbors = nearestNeighbors(ratings[-1], usersInFile, usersMap)
        sortedEntries = {}
        maxNeighbors = 20
        for user, entries in neighbors.items():
            if entries:
                sortedEntries[user] = sorted(entries.items(), key=lambda x: sum(x[1]) / len(x[1]))[:maxNeighbors]
            else:
                print(user)
        print("Finished clustering for file {}".format(i))
        estimatedRatingskmeans = []
        estimatedRatingskmode = []
        estimatedRating3 = []
        estimatedUserRatings = []
        with open(TEST_FILE_PATH.replace("_", str(i))) as f:
            beg = time.process_time()
            for line in f:
                entry = line.replace("\n", "").split("\t")
                trueRating = Rating(entry[0], entry[1], entry[2])
                sumScore = 0
                amtUsers = 0
                clusterIndex = -1
                clusterIndexMod = -1
                clusterIndex3 = -1
                """
                for index, cl in enumerate(clusters):
                    if next((x for x in cl if x == trueRating.user), None):
                        clusterIndex = index
                

                for index, cl in enumerate(clustersMod):
                    if next((x for x in cl if x == trueRating.user), None):
                        clusterIndexMod = index
                
                for index, cl in enumerate(clusters3):
                    if next((x for x in cl if x == trueRating.user), None):
                        clusterIndex3 = index
                """
                sumRatings = 0
                amt = 0
                modes = [0, 0, 0]
                sumRatings3 = 0
                userBasedRatings = []
                for user, lines in usersMap.items():
                    """
                    # For kmeans
                    if user in clusters[clusterIndex]:
                        for l in range(lines[0], lines[1]):
                            if ratings[-1][l].film == trueRating.film:
                                sumRatings += ratings[-1][l].rating
                                amt += 1
                    
                #for kmode
                    if user in clustersMod[clusterIndexMod]:
                        for l in range(lines[0], lines[1]):
                            if ratings[-1][l].film == trueRating.film:
                                modes[ratings[-1][l].categoryRating - 1] += 1
                    

                    # for method3
                    if user in clusters3[clusterIndex3]:
                        for l in range(lines[0], lines[1]):
                            if ratings[-1][l].film == trueRating.film:
                                sumRatings3 += ratings[-1][l].rating
                                amt += 1
                    """
                # for method 4
                for user, entry in sortedEntries[trueRating.user]:
                    othersRating = next(
                        (x for x in ratings[-1][usersMap[user][0]: usersMap[user][1]] if
                         x.film == trueRating.film),
                        None)
                    if othersRating:
                        userBasedRatings.append(othersRating.rating)

                calculatedRatings = -1
                mode = -1
                calculatedRatings3 = -1
                calculatedUserRatings = -1
                if sumRatings > 0:
                    calculatedRatings = sumRatings / amt
                if any([x > 0 for x in modes]):
                    mode = getMode(modes)
                if sumRatings3 > 0:
                    calculatedRatings3 = sumRatings3 / amt
                if userBasedRatings:
                    calculatedUserRatings = round(sum(userBasedRatings) / len(userBasedRatings), 0)
                # estimatedRatingskmeans.append((trueRating.rating, calculatedRatings))
                # estimatedRatingskmode.append((trueRating.categoryRating, mode))
                # estimatedRating3.append((trueRating.categoryRating, calculatedRatings3))
                estimatedUserRatings.append((trueRating.categoryRating, calculatedUserRatings))
            print(time.process_time() - beg)
            # removedClutterkmeans = [x for x in estimatedRatingskmeans if x[1] != -1]
            # removedClutterkmode = [x for x in estimatedRatingskmode if x[1] != -1]
            # removedClutter3 = [x for x in estimatedRating3 if x[1] != -1]
            removedClutterUserRating = [x for x in estimatedUserRatings if x[1] != -1]
            """
            print("******KMEANS*******")
            print("{} clusters pour le fichier {}: {} manquants sur 20000".format(k, i, len(estimatedRatingskmeans) - len(
                removedClutterkmeans)))
            avg = sum([abs(true - calculated) for true, calculated in removedClutterkmeans]) / len(removedClutterkmeans)
            variance = sum([(avg - abs(true - calculated)) ** 2 for true, calculated in removedClutterkmeans]) / (
                    len(removedClutterkmeans) - 1)
            print("moyenne de {} et variance de {}\n".format(avg, variance))
            
            print("*******KMODE*********")
            print("{} clusters pour le fichier {}: {} manquants sur 20000".format(k, i, len(estimatedRatingskmode) - len(
                    removedClutterkmode)))
            avg = sum([abs(true - calculated) for true, calculated in removedClutterkmode]) / len(removedClutterkmode)
            variance = sum([(avg - abs(true - calculated)) ** 2 for true, calculated in removedClutterkmode]) / (
                    len(removedClutterkmode) - 1)
            print("moyenne de {} et variance de {}\n".format(avg, variance))
            """

            """
            print("*******METHODE 3*********")
            print(
                "{} clusters pour le fichier {}: {} manquants sur 20000".format(k, i, len(estimatedRating3) - len(
                    removedClutter3)))
            avg = sum([abs(true - calculated) for true, calculated in removedClutter3]) / len(removedClutter3)
            variance = sum([(avg - abs(true - calculated)) ** 2 for true, calculated in removedClutter3]) / (
                    len(removedClutter3) - 1)
            print("moyenne de {} et variance de {}\n".format(avg, variance))
            """
            print("*******NEAREST NEIGHBOR*********")
            print(
                "{} clusters pour le fichier {}: {} manquants sur 20000".format(k, i, len(estimatedUserRatings) - len(
                    removedClutterUserRating)))
            avg = sum([abs(true - calculated) for true, calculated in removedClutterUserRating]) / len(removedClutterUserRating)
            variance = sum([(avg - abs(true - calculated)) ** 2 for true, calculated in removedClutterUserRating]) / (
                    len(removedClutterUserRating) - 1)
            print("moyenne de {} et variance de {}\n".format(avg, variance))
