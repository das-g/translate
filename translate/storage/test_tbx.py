from translate.storage import tbx, test_base


class TestTBXUnit(test_base.TestTranslationUnit):
    UnitClass = tbx.tbxunit


class TestTBXfile(test_base.TestTranslationStore):
    StoreClass = tbx.tbxfile

    def test_basic(self):
        tbxfile = tbx.tbxfile()
        assert tbxfile.units == []
        tbxfile.addsourceunit("Bla")
        assert len(tbxfile.units) == 1
        newfile = tbx.tbxfile.parsestring(bytes(tbxfile))
        print(bytes(tbxfile))
        assert len(newfile.units) == 1
        assert newfile.units[0].source == "Bla"
        assert newfile.findunit("Bla").source == "Bla"
        assert newfile.findunit("dit") is None

    def test_source(self):
        tbxfile = tbx.tbxfile()
        tbxunit = tbxfile.addsourceunit("Concept")
        tbxunit.source = "Term"
        newfile = tbx.tbxfile.parsestring(bytes(tbxfile))
        print(bytes(tbxfile))
        assert newfile.findunit("Concept") is None
        assert newfile.findunit("Term") is not None

    def test_target(self):
        tbxfile = tbx.tbxfile()
        tbxunit = tbxfile.addsourceunit("Concept")
        tbxunit.target = "Konsep"
        newfile = tbx.tbxfile.parsestring(bytes(tbxfile))
        print(bytes(tbxfile))
        assert newfile.findunit("Concept").target == "Konsep"

    def test_setid(self):
        tbxfile = tbx.tbxfile()
        tbxunit = tbxfile.addsourceunit("Concept")
        tbxunit.setid("testid")
        newfile = tbx.tbxfile.parsestring(bytes(tbxfile))
        print(bytes(tbxfile))
        assert newfile.findunit("Concept").getid() == "testid"

    def test_indent(self):
        tbxfile = tbx.tbxfile()
        tbxunit = tbxfile.addsourceunit("Concept")
        tbxunit.setid("testid")
        assert (
            bytes(tbxfile).decode()
            == """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE martif PUBLIC "ISO 12200:1999A//DTD MARTIF core (DXFcdV04)//EN" "TBXcdv04.dtd">
<martif type="TBX" xml:lang="en">
    <martifHeader>
        <fileDesc>
            <sourceDesc>
                <p>Translate Toolkit</p>
            </sourceDesc>
        </fileDesc>
    </martifHeader>
    <text>
        <body>
            <termEntry id="testid">
                <langSet xml:lang="en"><tig><term>Concept</term></tig></langSet>
            </termEntry>
        </body>
    </text>
</martif>
"""
        )
