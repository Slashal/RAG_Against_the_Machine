# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  __main__.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 17:56:27 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 17:11:00 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Module entry point for `uv run python -m src`."""

from src.cli.cli import menu


def main() -> None:
    """Run the CLI entry point and report a friendly error on failure."""

    try:
        menu()
    except Exception as exc:  # pragma: no cover - defensive CLI guard
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
