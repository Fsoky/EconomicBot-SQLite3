from environs import Env

env = Env()
env.read_env()

TOKEN = env.str("TOKEN")
