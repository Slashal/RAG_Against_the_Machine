# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  __main__.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 17:56:27 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 16:31:47 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from src.cli.cli import menu


def main() -> None:
    try:
        menu()
    except Exception as exc:  # pragma: no cover - defensive CLI guard
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
