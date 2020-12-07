from application.app import redis_pool, logger
import redis


def redis_set(key: str, value: str, second: int) -> bool:
    try:
        red = redis.Redis(connection_pool=redis_pool)
        red.set(key, value, ex=second)
        # print(red.get(key))
    except Exception as e:
        logger.error(str(e))
        return False
    return True


def redis_del(key: str) -> bool:
    try:
        red = redis.Redis(connection_pool=redis_pool)
        red.delete(key)
    except Exception as e:
        logger.error(str(e))
        return False
    return True


def redis_exist_del(key: str) -> bool:
    try:
        red = redis.Redis(connection_pool=redis_pool)
        res = red.exists(key)
    except Exception as e:
        logger.error(str(e))
        return False
    if res == 1:
        try:
            red.delete(key)
        except Exception as e:
            logger.error(str(e))
            return False
        return True
    return False


def redis_exist_prolong(key: str, second: int) -> str:
    try:
        red = redis.Redis(connection_pool=redis_pool)
        res = red.exists(key)
    except Exception as e:
        logger.error(str(e))
        return ''
    if res == 1:
        try:
            res = red.get(key)
            red.expire(key, second)
        except Exception as e:
            logger.error(str(e))
            return ''
        return res.decode()
    return ''


def redis_get_set(key: str, value: str, second: int) -> str:
    # res = ''
    try:
        red = redis.Redis(connection_pool=redis_pool)
        res = red.getset(key, value)
        red.expire(key, second)
        # print(red.get(key))
    except Exception as e:
        logger.error(str(e))
        return ''
    return res


def redis_get(key: str) -> str:
    # res = ''
    try:
        red = redis.Redis(connection_pool=redis_pool)
        res = red.get(key)
    except Exception as e:
        logger.error(str(e))
        return ''
    return res