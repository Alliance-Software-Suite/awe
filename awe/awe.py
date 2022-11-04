from args import get_args
from auditor import do_audit
from cfg import get_config

args = get_args()
config = get_config(args)

do_audit(config)
