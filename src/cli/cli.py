# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  cli.py                                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 14:05:45 by hguesne         #+#    #+#               #
#  Updated: 2026/09/28 14:31:26 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import fire
from pathlib import Path


class CLI:
    def __init__(self, inpath: str, outpath: str):
        self.inpath = inpath
        self.outpath = outpath

    def index(self):
        pass


def menu() -> str:
    inpath = input("Enter the input path: ")
    outpath = input("Enter the output path: ")
    input_dir = Path(inpath)
    output_dir = Path(outpath)

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    fire.Fire(CLI(inpath, outpath))
