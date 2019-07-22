from gym.envs.registration import register

register(
    id='n-joints-v0',
    entry_point='gym_scalable.envs:NJointArm',
)

register(
    id='n-chasers-v0',
    entry_point='gym_scalable.envs:Chasers',
)
