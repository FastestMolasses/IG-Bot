import config
import random

from time import sleep
from instagram import Instagram


LIKE_STEP = 2
COMMENT_STEP = 15
FOLLOW_STEP = 20


def randSleep():
    sleep(random.randint(2, 5))


def likePost(ig: Instagram, data: dict):
    ig.likePost(data['id'])
    mediaType = 'video' if data['is_video'] else 'image'
    shortcode = data['shortcode']
    print(f'∘ Liked {mediaType} | https://www.instagram.com/p/{shortcode}')


def commentPost(ig: Instagram, data: dict):
    c = random.choice(config.COMMENTS)
    ig.postComment(data['id'], c)
    shortcode = data['shortcode']
    print(f'∘ Posted comment | https://www.instagram.com/p/{shortcode}')


def followPoster(ig: Instagram, shortcode: str):
    x = ig.getPostInfo(shortcode)
    sleep(5)

    user = x['username']
    ig.followUser(user)
    print(f'∘ Followed {user} | https://www.instagram.com/{user}')


def main():
    print('- -' * 14)
    print(f'|\tSession started {config.INSTAGRAM_USERNAME}\t |')
    print('- -' * 14, end='\n\n')

    ig = Instagram()

    # --------------------------------------

    tagFeed = []
    for i in config.TAGS:
        print(f'∘ Getting posts for #{i}')
        tagFeed.extend(ig.searchTagFeed(i, count=50))
        randSleep()

    for i, x in enumerate(tagFeed):
        if i % LIKE_STEP == 0:
            likePost(ig, x)
        elif i % COMMENT_STEP == 0:
            commentPost(ig, x)
        elif i % FOLLOW_STEP == 0:
            followPoster(ig, x['shortcode'])

        randSleep()

    # --------------------------------------

    print(f'∘ Getting timeline posts')
    timeline = ig.getTimeline(count=200)
    for i, x in enumerate(timeline):
        if i % LIKE_STEP == 0:
            likePost(ig, x)
        elif i % COMMENT_STEP == 0:
            commentPost(ig, x)

        randSleep()

    # --------------------------------------

    print('- -' * 14)
    print(f'|\t     Finished session!\t\t |')
    print('- -' * 14, end='\n\n')


if __name__ == '__main__':
    main()
