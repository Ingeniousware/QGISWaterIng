from ..inpProcessing.sectionINPAbstract import sectionINPAbstract


class sectionBackdrop(sectionINPAbstract):
    def __init__(self):
        # Constructor.
        super(sectionBackdrop, self).__init__()

    def ProcessCoordinatesConvertion(self, out_file, line):
        new_unit = "Degrees"
        new_dimensions = "-180\t\t" + "-90\t\t" + "180\t\t" "90"

        try:
            if line.strip().startswith("DIMENSIONS"):
                updated_line = f"DIMENSIONS\t{new_dimensions}"
                out_file.write(updated_line + "\n")

            elif line.strip().startswith("UNITS"):
                updated_line = f"UNITS\t\t{new_unit}"
                out_file.write(updated_line + "\n")
            else:
                out_file.write(line + "\n")
        except ValueError:
            out_file.write(line + "\n")
