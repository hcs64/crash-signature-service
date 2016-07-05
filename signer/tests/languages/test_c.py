import mock

from signer.languages.c import CSignatureTool


class TestSignatureToolBase(object):
    @staticmethod
    def get_instance(
        irrelevant=('ignored1',),
        prefix=('pre1', 'pre2', 'sentinel1', 'sentinel2', 'foo32\.dll',),
        trim_dll=('foo32\.dll.*',),
        sentinels=('sentinel1', ('sentinel2', lambda x: 'bar' in x))
    ):
        with mock.patch('signer.languages.c.siglists') as m_siglists:
            m_siglists.IRRELEVANT_SIGNATURE_RE = irrelevant
            m_siglists.PREFIX_SIGNATURE_RE = prefix
            m_siglists.TRIM_DLL_SIGNATURE_RE = trim_dll
            m_siglists.SIGNATURE_SENTINELS = sentinels

            return CSignatureTool()

    def test_generate_simple(self):
        inst = self.get_instance()

        frames = [
            'foo',
            'bar',
        ]
        signature, _ = inst.generate(frames)
        assert signature == 'foo'

    def test_generate_with_prefix(self):
        inst = self.get_instance()

        frames = [
            'pre1',
            'pre2',
            'foo',
            'bar',
        ]
        signature, _ = inst.generate(frames)
        assert signature == 'pre1 | pre2 | foo'

    def test_generate_with_sentinel(self):
        inst = self.get_instance()

        frames = [
            'pre1',
            'sentinel1',
            'pre2',
            'foo',
            'bar',
        ]
        signature, _ = inst.generate(frames)
        assert signature == 'sentinel1 | pre2 | foo'

    def test_generate_with_advanced_sentinel(self):
        inst = self.get_instance()

        frames = [
            'pre1',
            'sentinel2',
            'foo',
            'sentinel1',
            'foo',
            'bar',
        ]
        signature, _ = inst.generate(frames)
        assert signature == 'sentinel2 | foo'

        # Note that 'bar' is missin,. so 'sentinel2' is not a valid sentinel.
        frames = [
            'pre1',
            'sentinel2',
            'foo',
            'sentinel1',
            'foo',
        ]
        signature, _ = inst.generate(frames)
        assert signature == 'sentinel1 | foo'

    def test_generate_with_irrelevant(self):
        inst = self.get_instance()

        frames = [
            'ignored1',
            'pre1',
            'pre2',
            'foo',
            'bar',
        ]
        signature, _ = inst.generate(frames)
        assert signature == 'pre1 | pre2 | foo'

        frames = [
            'pre1',
            'pre2',
            'ignored1',
            'foo',
            'bar',
        ]
        signature, _ = inst.generate(frames)
        assert signature == 'pre1 | pre2 | foo'

    def test_generate_with_trim_dll(self):
        inst = self.get_instance()

        frames = [
            'foo32.dll@0x1121',
            'foo32.dll@0x0',
            'foo32.dll@0xd2a03',
            'foo',
            'bar',
        ]
        signature, _ = inst.generate(frames)
        assert signature == 'foo32.dll | foo'

        frames = [
            'pre1',
            'foo32.dll@0x1121',
            'foo32.dll@0x0',
            'foo32.dll@0xd2a03',
            'foo',
            'bar',
        ]
        signature, _ = inst.generate(frames)
        assert signature == 'pre1 | foo32.dll | foo'

    def test_generate_no_frames(self):
        inst = self.get_instance()

        # No frames, no crashed thread number.
        frames = []
        signature, notes = inst.generate(frames)
        assert signature == 'EMPTY: no crashing thread identified'
        assert len(notes) == 1
        assert 'we do not know which thread crashed' in notes[0]

        # No frames, but a crashed thread number.
        frames = []
        signature, notes = inst.generate(frames, crashed_thread=12)
        assert signature == 'EMPTY: no frame data available'
        assert len(notes) == 1
        assert 'no good data for the crashing thread (12)' in notes[0]

        # Only irrelevant frames, no crashed thread number.
        frames = ['ignored1']
        signature, notes = inst.generate(frames)
        assert signature == 'EMPTY: no crashing thread identified'
        assert len(notes) == 1
        assert 'we do not know which thread crashed' in notes[0]

        # Only irrelevant frames, and a crashed thread number.
        frames = ['ignored1']
        signature, notes = inst.generate(frames, crashed_thread=12)
        assert signature == 'ignored1'
        assert len(notes) == 1
        assert 'no good data for the crashing thread (12)' in notes[0]
