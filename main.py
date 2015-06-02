from SBB.sbb import SBB
from SBB.config import Config
from examples import thyroid_config

if __name__ == "__main__":
    # # To run SBB with a predefined parameter set, uncomment the next line. More defaults are available in /examples
    # Config.USER = thyroid_config.THYROID_DEFAULT

    Config.check_parameters()
    SBB().run()