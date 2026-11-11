"""build_rainfall.py: KMA hourly CSV parsing and the reproduce-before-write guard."""
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta
import io
from pathlib import Path
import tempfile
import unittest

from scripts.build_rainfall import read_hourly, gaps, main


def day_rows(station, date, values, flag_column=False):
    """24 rows stamped 01:00 … next day 00:00, the KMA hourly layout."""
    start = datetime.strptime(date, "%Y-%m-%d") + timedelta(hours=1)
    rows = []
    for offset in range(24):
        stamp = start + timedelta(hours=offset)
        value = values.get(offset + 1, "")
        rows.append(f"{station},서울,{stamp:%Y-%m-%d %H:%M},{value}" + (",9" if value == "missing" else ",") * flag_column)
    return [row.replace("missing", "") for row in rows]


class BuildRainfallTests(unittest.TestCase):
    def write(self, folder, lines, header="지점,지점명,일시,강수량(mm)"):
        path = Path(folder) / "hourly.csv"
        path.write_text("\n".join([header] + lines) + "\n", encoding="cp949")
        return path

    def test_midnight_is_hour_24_and_blank_is_no_rain(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, day_rows(108, "2025-07-15", {23: 41.5, 24: 15}))
            samples = read_hourly([path])[108]
        self.assertEqual(len(samples), 24)
        self.assertIn(("2025-07-15", 24, 15.0), samples)
        self.assertIn(("2025-07-15", 1, 0.0), samples)

    def test_qc_flag_9_is_missing_not_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, day_rows(108, "2025-07-15", {5: "missing"}, flag_column=True),
                              header="지점,지점명,일시,강수량(mm),강수량 QC플래그")
            samples = read_hourly([path])[108]
        self.assertEqual(len(samples), 23)
        self.assertIn("2025-07-15(1시간)", gaps(samples))

    def test_incomplete_downloads_never_overwrite_rainfall_file(self):
        with tempfile.TemporaryDirectory() as folder:
            source = self.write(folder, day_rows(424, "2025-07-10", {5: 52.5}))
            output = Path(folder) / "rainfall.csv"
            output.write_text("자치구\n원본\n", encoding="utf-8-sig")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as messages:
                self.assertEqual(main([str(source), "--output", str(output)]), 1)
            self.assertIn("관측이 빠진 날", messages.getvalue())
            self.assertEqual(output.read_text(encoding="utf-8-sig"), "자치구\n원본\n")


if __name__ == "__main__":
    unittest.main()
