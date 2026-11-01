"""Animation catalog and behavior tuning. Durations are milliseconds."""
ANIMATIONS = {
    'idle': {'file': 'LXHflower.gif'}, 'walk_left': {'file': 'LXHroll.gif'},
    'walk_right': {'file': 'LXHroll1.gif'}, 'lift': {'file': 'LXHmiao.gif'},
    'fall': {'file': 'LXHmiao.gif'}, 'run_left': {'file': 'LXHrun.gif'},
    'run_right': {'file': 'LXHrunright.gif'}, 'eat': {'file': 'LXHeat.gif'},
    'work': {'file': 'LXHwork.gif'}, 'collectible': {'file': 'LXHheixiu.gif'},
}
for key, label, filename in [
    ('fish','钓鱼','LXHfish.gif'), ('ski','滑雪','LXHski.gif'),
    ('happy','开心','LXHhappy.gif'), ('play','玩耍','LXHplay2.gif'),
    ('money','数钱','LXHmoney.gif'), ('bored','无聊','LXHbored.gif'),
    ('guitar','弹吉他','LXHguitar.gif'), ('laugh','大笑','LXHlaugh.gif'),
    ('tail','背对','LXHtail.gif'),
]:
    ANIMATIONS[key] = {'label': label, 'file': filename, 'menu': True, 'weight': 1}
PARAMS = {
    'collect_interval': 180000, 'collect_check': 100,
    'random_interval': 2220000, 'random_duration': 180000,
    'direction_interval': 3000, 'walk_speed': 10, 'walk_tick': 100,
    'fall_speed': 5, 'fall_tick': 30, 'collect_speed': 30, 'collect_tick': 50,
    'hunger_interval': 120000, 'eat_interval': 1000,
    'clock_tick': 100, 'reminder_tick': 1000,
}
