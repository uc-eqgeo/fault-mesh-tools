#!/bin/bash
./fault_local_to_cubit.py --in_root=../data/cfm-multi-local-stl --out_directory=../data/cfm-multi-global-cubit --in_qualifier=_local --out_qualifier=_global_cubit --resolution=1500.0 --smoothing=1.8 --output_global --verbose
