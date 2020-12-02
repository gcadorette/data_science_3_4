# Guillaume Cadorette - cadg3202 - 17 040 202

DATA_FILE_PATH = "data/u.item"
USER_FILE_PATH = "data/u.user"
BASE_FILE_PATH = "data/u_.base"
TEST_FILE_PATH = "data/u_.test"
EPSILON = 0.01  # seuil de convergence


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


def kmeans(amtOfClusters, values):
    clusters = []
    clustersMid = []
    for ind in range(amtOfClusters + 1):
        clustersMid.append(values.keys()[ind])
        clusters.append([])
    for _ in amtOfClusters:
        for key, value in values.items():
            pass
            # TODO: FAIRE LE ACTUAL KMEANS LMAO
            # EN GROS ON COMPARE LES DISTANCES SUR LES FILMS QUE LES DEUX ONT RATE
            # FACILE FACILE CITRON PRESSE



"""
def distance(rating1: Rating, rating2: Rating):
    ageDiff = abs(rating1.user.age - rating2.user.age) ** 2
    sexDiff = abs(rating1.user.sex - rating2.user.sex) ** 2
    jobDiff = 1 if rating1.user.job != rating2.user.job else 0

    yearDiff = abs(rating1.film.year - rating2.film.year) ** 2
    genreDiff = 0
    for index in len(rating1.film.genre):
        genreDiff += 1 if rating1.film.genre[index] != rating2.film.genre[index] else 0
    genreDiff = genreDiff ** 2
    ratingDiff = abs(rating1.rating - rating2.rating) ** 2

    return ratingDiff, genreDiff, yearDiff, jobDiff, sexDiff, ageDiff
"""

def distance(rating1: Rating, rating2: Rating):



def distanceRating(rating1, rating2):
    pass


def distanceUser(user1, user2):
    ageDiff = abs(user1.age - user2.age) ** 2
    sexDiff = abs(user1.sex - user2.sex) ** 2
    jobDiff = 1 if user1.job != user2.job else 0
    return [ageDiff, sexDiff, jobDiff]


if __name__ == "__main__":
    """
    films = {}
    users = {}
    with open(DATA_FILE_PATH) as f:
        for line in f:
            entry = line.replace("\n", "").split("|")
            films[entry[0]] = Film(entry[2].split("-")[-1], "".join(entry[5:]).replace("|", ""))
    with open(USER_FILE_PATH) as f:
        for line in f:
            entry = line.replace("\n", "").split("|")
            users[entry[0]] = User(entry[0], entry[1], entry[2], entry[3])
    """
    ratings = []
    for i in range(1, 6):
        usersInFile = []
        filmsInFile = []
        with open(BASE_FILE_PATH.replace("_", str(i))) as f:
            ratings.append({})
            for line in f:
                entry = line.split("\t")
                # ratings[-1].append(Rating(users[entry[0]], films[entry[1]], entry[2]))
                # ratings[-1].append(entry[0], entry[1], entry[2])
                ratings[-1][entry[0]] = Rating(entry[0], entry[1], entry[2])
        for k in range(2, 13):
            kmeans(k, ratings[-1])
    print("me:)")
