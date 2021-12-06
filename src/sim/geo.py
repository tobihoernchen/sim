from .buffer import Buffer, BufferWorkOn
from .part import Part
import numpy as np

cond_geo = lambda x, **kwargs: x == "Geo"


def mod_geo(x, **kwargs):
    x.check("Geo")
    return x


class Geo(Buffer):
    def __init__(
        self, name, group_input_parts, group_output_part, time, check_sequence=False
    ):
        max_parts = len(group_input_parts)
        super().__init__(name, max_parts)
        self.input_parts = group_input_parts
        self.output_part = group_output_part
        self.check_sequence = check_sequence
        self.programs.append(
            BufferWorkOn(
                self.name + "_Geo",
                time,
                parent=self,
                modifier=mod_geo,
                condition=cond_geo,
            )
        )

    def get_free_spot(self, reserved=False, **kwargs):
        if "part" in kwargs.keys():
            part = kwargs["part"]
        else:
            return False
        if not self.parts[0] == self.output_part:
            for i in range(len(self.parts)):
                if (
                    not self.parts[i]
                    and self.reserved[i] == reserved
                    and part == self.input_parts[i]
                ):
                    return i
        return False

    def get_part_to_give(self, part="", reserved=False, **kwargs):
        if self.parts[0]:
            if (
                self.output_part == self.parts[0]
                and part == self.parts[0]
                and not "Geo" == self.parts[0]
                and self.reserved[0] == reserved
            ):
                return 0
        return False

    def receive(self, part, **kwargs):
        out = super().receive(part, **kwargs)
        if out and self.fill == self.max_parts and not any(self.reserved):
            self.fill << 1
            new_type = "".join(list(np.unique([prt.type for prt in self.parts])))
            self.parts[0] = Part(
                group=self.output_part,
                type=new_type,
                seq_nr=self.parts[0].seq_nr,
                planned=["Geo"],
            )

            self.parts[1:] = [False for _ in self.parts[1:]]
        return out


class DoubleGeo(Buffer):
    def __init__(
        self,
        name,
        group_input_parts,
        group_output_part1,
        group_output_part2,
        time,
        check_sequence=False,
    ):
        max_parts = max(len(group_input_parts), 2)
        super().__init__(name, max_parts)
        self.input_parts = group_input_parts
        self.output_part1 = group_output_part1
        self.output_part2 = group_output_part2
        self.check_sequence = check_sequence
        self.programs.append(
            BufferWorkOn(
                self.name + "_Geo",
                time,
                parent=self,
                modifier=mod_geo,
                places=[0],
                condition=cond_geo,
            )
        )
        self.programs.append(
            BufferWorkOn(
                self.name + "_Geo",
                time,
                parent=self,
                modifier=mod_geo,
                places=[1],
                condition=cond_geo,
            )
        )

    def get_free_spot(self, reserved=False, **kwargs):
        if "part" in kwargs.keys():
            part = kwargs["part"]
        else:
            return False
        if (
            not self.parts[0] == self.output_part1
            and not self.parts[1] == self.output_part2
        ):
            for i in range(len(self.parts)):
                if (
                    not self.parts[i]
                    and self.reserved[i] == reserved
                    and part == self.input_parts[i]
                ):
                    return i
        return False

    def get_part_to_give(self, part="", reserved=False, **kwargs):
        if self.parts[0]:
            if (
                self.output_part1 == self.parts[0]
                and part == self.parts[0]
                and not "Geo" == self.parts[0]
                and self.reserved[0] == reserved
            ):
                return 0
        if self.parts[1]:
            if (
                self.output_part2 == self.parts[1]
                and part == self.parts[1]
                and not "Geo" == self.parts[1]
                and self.reserved[1] == reserved
            ):
                return 1
        return False

    def receive(self, part, **kwargs):
        out = super().receive(part, **kwargs)
        if out and self.fill == len(self.input_parts) and not any(self.reserved):
            self.fill << 2
            new_type = "".join(
                list(
                    np.unique(
                        [self.parts[i].type for i in range(len(self.input_parts))]
                    )
                )
            )
            self.parts[0] = Part(
                group=self.output_part1,
                type=new_type,
                seq_nr=self.parts[0].seq_nr,
                planned=["Geo"],
            )
            self.parts[1] = Part(
                group=self.output_part2,
                type=new_type,
                seq_nr=self.parts[0].seq_nr,
                planned=["Geo"],
            )

            self.parts[2:] = [False for _ in self.parts[1:]]
        return out
