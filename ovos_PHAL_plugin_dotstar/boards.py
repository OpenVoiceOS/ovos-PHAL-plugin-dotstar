from adafruit_dotstar import DotStar
import board

RESPEAKER2MIC = DotStar(board.D11, board.D10, 3, brightness=0.2)
RESPEAKER4_6_8MIC = DotStar(board.D11, board.D10, 12, brightness=0.2)
# RESPEAKER6MIC = DotStar(board.D11, board.D12, 12, brightness=0.2)

ADAFRUIT2MIC = DotStar(board.D6, board.D5, 3, brightness=0.2)

preconfig_boards = {
    "wm8960": [RESPEAKER2MIC],  # ADAFRUIT2MIC],
    "respeaker2mic": RESPEAKER2MIC,
    "respeaker4mic": RESPEAKER4_6_8MIC,
    "respeaker6mic": RESPEAKER4_6_8MIC,
    "respeaker8mic": RESPEAKER4_6_8MIC,
    "adafruit2mic": ADAFRUIT2MIC}
