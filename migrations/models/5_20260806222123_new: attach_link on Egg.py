from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "egg" ADD "attach_link" TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "egg" DROP COLUMN "attach_link";"""


MODELS_STATE = (
    "eJztml9v4jgQwL9KlKeu1FvRFGiPN6C0y20Lqza7t9rTyTKJCVaNTW2zFPX47is7/0PCEa"
    "6g0ssbjGcS5+fxjGeSF3PKXETEx57nmS3jxaRwisyWkRSfGiaczWKhEkg4IloPBQojITl0"
    "pNkyxpAIdGqYLhIOxzOJGTVbBp0TooTMEZJj6sWiOcVPcwQk85CcIG62jL/+PjVMTF30jE"
    "T4d/YIxhgRNzVJ7Kp7azmQy5mW9am81orqbiPgMDKf0lh5tpQTRiNtTKWSeogiDiVSl5d8"
    "rqavZhc8ZPhE/kxjFX+KCRsXjeGcyMTjjkAsMwEYDG3w0LMBMEsAchhVcDGVisaL6akp/G"
    "ad1S/ql+fN+uWpYeppRpKLlX/rGIxvqPEMbHOlx6GEvoZmHEOV6FmuY7XRcwHXUD9DVkie"
    "JRtyTKANwEVkQ5UYbexOB2C7AZzd+26rK0+FeCJKMPjWvu9+at+f3LW/f9Ajy2Dkdji4Cd"
    "UZh46/Uwbd22FHs49ZQymhMwEzKCdlkGfMKvI7k59AkUO+O4F8I/nQbE/kDxpOpvAZEEQ9"
    "OTFbRrO+YQuEDt+sf8gADkYsPZQLmmD6uIOLh2aVi5d3cSrGi3XkHcYIgjSfemiSwT1ijG"
    "zh2Gt5cptoHkkOG847w+FtKpx3+lmkX+86vfuTM+3r4olgiZIJNObscKSYAJiTNq+gRBJP"
    "UT7utGUGuhuYfgx/7GsF9hlcOILukJJlENQ25df+Xe/Bbt99Sa3KVdvuqRErlWBD6UkzE4"
    "iiixh/9u1Phvpr/BgOehovE9Lj+o6xnv3DVHOCc8kAZQsA3UT8DaUhtdSqIxfvtugpw2rN"
    "38qah/siseiBx2Z2OuMgr+7oYK+w9Ejb/XsJcgw7269Cfres8/MLq3bevGzULy4al7WoHF"
    "kf2lSXdPo3KrKmVnY91DKOPUxL80+ZVfhL4VfF9/gxt1IM3Hp9La4ZR9ijn9FSr0efCgmp"
    "g3LoB22GrwLxI9wEgT/H0jh3cLiIGhaZ/c8ocBFB/nGi237otq96Zo6bvwLXmzn2t8M7BZ"
    "va2Plclf+OoPO4gNwFKUdWI8xiGUmkuz40taZZCaTQ03jUc6hZp8DnNNSiFSluqXmRyptp"
    "qm0Krq8ZVd9CY+0gKa24/ZacfIl6OWNW1cvl62VMf6oarwT02KLiXZ43gdQr03sL9XdivV"
    "OGM5HeTPtvuzW26Lo1CptujbWeGyFsAeYCcZAPeWMTKMf6gP2gMOIfVTto7ZBcfOpIdBA8"
    "T+QsTWB1/fkeEVgQz9Nv597J4W61zwOZrjByzmNh5VF8HFMboTqN/U9PY1WO2leOGkFKkV"
    "syNcVG1RuKKiUdeUpqI46dSV5SCkY2piUY67yZNkH17c1//PbmJ+Iit/AvrooSJocrjA72"
    "PYLV2CbtWI3ixKPHMuXRbFbqmw9f/R3SPavVtqB7VqsV0tVjmdfhjErkt//ShP94GA4K3o"
    "/FJtkXotiRxj8GweIYX5KtiuEqGJs/J8s2TzKvM9UFVEelROn5+sls9Quq8nAk"
)
