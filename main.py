import config
import random

from time import sleep, time
from datetime import datetime
from instagram import Instagram


LIKE_STEP = 2
COMMENT_STEP = 15
FOLLOW_STEP = 20


def getTimeStamp():
    ts = time()
    return datetime.fromtimestamp(ts).strftime('%H:%M:%S')


def randSleep():
    sleep(random.randint(4, 10))


def likePost(ig: Instagram, data: dict):
    ig.likePost(data['id'])
    mediaType = 'video' if data['is_video'] else 'image'
    shortcode = data['shortcode']
    print(
        f'∘ [{getTimeStamp()}] Liked {mediaType} | https://www.instagram.com/p/{shortcode}')

    LIKE_STEP = random.randint(2, 4)


def commentPost(ig: Instagram, data: dict):
    if len(config.COMMENTS) <= 0:
        return
    
    c = random.choice(config.COMMENTS)
    ig.postComment(data['id'], c)
    shortcode = data['shortcode']
    print(
        f'∘ [{getTimeStamp()}] Posted comment | https://www.instagram.com/p/{shortcode}')

    COMMENT_STEP = random.randint(13, 15)


def followPoster(ig: Instagram, shortcode: str):
    x = ig.getPostInfo(shortcode)
    sleep(5)

    user = x['username']
    ig.followUser(user)
    print(f'∘ [{getTimeStamp()}] Followed {user} | https://www.instagram.com/{user}')

    FOLLOW_STEP = random.randint(14, 20)


def unfollowPoster(ig: Instagram, shortcode: str):
    x = ig.getPostInfo(shortcode)
    sleep(5)

    user = x['username']
    ig.unfollowUser(user)
    print(
        f'∘ [{getTimeStamp()}] Unfollowed {user} | https://www.instagram.com/{user}')


def main():
    print('- -' * 14)
    print(f'|\tSession started {config.INSTAGRAM_USERNAME}\t |')
    print('- -' * 14, end='\n\n')

    ig = Instagram()

    # --------------------------------------

    print(f'\n∘ [{getTimeStamp()}] Getting timeline posts', end='\n\n')
    timeline = ig.getTimeline(count=200)
    for i, x in enumerate(timeline):
        if i % LIKE_STEP == 0:
            likePost(ig, x)
        if i % COMMENT_STEP == 0:
            commentPost(ig, x)
        if i % unfollowPoster == 0:
            unfollowPoster(ig, x['shortcode'])

        randSleep()

    # --------------------------------------

    tagFeed = []
    for i in config.TAGS:
        print(f'∘ [{getTimeStamp()}] Getting posts for #{i}')
        tagFeed.extend(ig.searchTagFeed(i.replace('#', ''), count=200))
        randSleep()
    print()

    for i, x in enumerate(tagFeed):
        if i % LIKE_STEP == 0:
            likePost(ig, x)
        if i % COMMENT_STEP == 0:
            commentPost(ig, x)
        if i % FOLLOW_STEP == 0:
            followPoster(ig, x['shortcode'])

        randSleep()

    # --------------------------------------

    print('- -' * 14)
    print(f'|\t     Finished session!\t\t |')
    print('- -' * 14, end='\n\n')


if __name__ == '__main__':
    main()
