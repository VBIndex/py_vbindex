#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Lucas Costa Campos <l.campos@fz-juelich.de>
#
# Distributed under terms of the GNU license.

import argparse
import multiprocessing
import nibabel
import numpy as np
import vb_toolbox.io as io
import vb_toolbox.vb_index as vb

def create_parser():
    # Get some CLI information
    parser = argparse.ArgumentParser(description='Calculate the Vogt-Bailey index of a dataset.')
    parser.add_argument('-j', '--jobs', metavar='N', type=int, nargs=1,
                        default=[multiprocessing.cpu_count()], help="""Maximum
                        number of jobs to be used. If abscent, one job per CPU
                        will be spawned""")

    parser.add_argument('-n', '--norm', metavar='norm', type=str, nargs=1,
                        default=["geig"], help="""Laplacian norm to be
                        used. Defaults to unnorm""")

    parser.add_argument('-c', '--clusters', metavar='file', type=str, nargs=1, default=None,
                        help="""File containing the surface clusters.""")

    parser.add_argument('-fb', '--full-brain', action='store_true',
                        help="""Calculate full brain spectral reordering.""")

    requiredNamed = parser.add_argument_group('required named arguments')

    requiredNamed.add_argument('-s', '--surface', metavar='file', type=str,
                               nargs=1, help="""File containing the surface
                                              mesh""", required=True)

    requiredNamed.add_argument('-d', '--data', metavar='file', type=str,
                               nargs=1, help="""File containing the data over
                                              the surface""", required=True)

    requiredNamed.add_argument('-l', '--label', metavar='file', type=str,
                               nargs=1, help="""File containing the labels to
                                              identify the cortex, rather than
                                              the medial brain structures""",
                                              required=True)

    requiredNamed.add_argument('-o', '--output', metavar='file', type=str,
                               nargs=1, help="""Base name for the
                                              output files""", required=True)


    # args = parser.parse_args()

    return parser


def main():

    parser = create_parser()
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        quit()
    n_cpus = args.jobs[0]
    # Read the initial mesh, and run clustering on it
    # nib_surf, vertices, faces = io.open_gifti_surf("./100206.L.very_inflated_MSMAll.32k_fs_LR.surf.gii")
    nib_surf, vertices, faces = io.open_gifti_surf(args.surface[0])
    # Read labels
    # _, labels = io.open_gifti('../core-data-and-script/L.atlasroi.32k_fs_LR.shape.gii')
    _, labels = io.open_gifti(args.label[0])
    cort_index = np.array(labels, np.bool)

    # nib = nibabel.load("./trial_2/REAL_DATA.func.gii")
    nib = nibabel.load(args.data[0])
    cifti = nib.darrays[0].data

    if args.full_brain:
        print("Performing reordering of the full brain")
        Z = np.ones(len(vertices), dtype=np.int)
        result = vb.vb_cluster(vertices, faces, nib_surf, n_cpus, cifti, Z, args.norm[0], cort_index, args.output[0] + "." + args.norm[0])
    elif args.clusters is None:
        print("Running normal version")
        result = vb.vb_index(vertices, faces, nib_surf, n_cpus, cifti, args.norm[0], cort_index, args.output[0] + "." + args.norm[0])

    else:
        print("Running cluster version")
        nib, Z = io.open_gifti(args.clusters[0])
        Z = np.array(Z, dtype=np.int)
        result = vb.vb_cluster(vertices, faces, nib_surf, n_cpus, cifti, Z, args.norm[0], cort_index, args.output[0] + "." + args.norm[0])


if __name__ == "__main__":
    main()
