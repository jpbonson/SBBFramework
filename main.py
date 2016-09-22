from optparse import OptionParser
from SBB.sbb import SBB
from SBB.config import Config

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--config_file", dest="config_file",
                      help="configuration file that will be used by SBB", 
                      default="SBB/configs/default_config.json")
    (options, args) = parser.parse_args()
    
    Config.load_config(options.config_file)
    Config.check_parameters()
    SBB().run()