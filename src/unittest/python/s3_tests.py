from mock import Mock
from unittest2 import TestCase
from botocore.response import StreamingBody
from generic_similarity_search.parser.provider.implementations.s3 import S3


class TestS3(TestCase):
    def test_should_work_correctly(self):
        s3_url = "s3://eimer/verzeichnis/"
        self.assertEqual(S3()._get_s3_path(s3_url), "eimer/verzeichnis/")

    def test_should_work_without_s3_protocol(self):
        s3_url = "eimer/verzeichnis/"
        self.assertEqual(S3()._get_s3_path(s3_url), "eimer/verzeichnis/")

    def test_should_work_correctly_with_beginning_slash(self):
        s3_url = "/eimer/verzeichnis/"
        self.assertEqual(S3()._get_s3_path(s3_url), "eimer/verzeichnis/")

    def test_should_include_last_line_with_new_line_symbol(self):
        body = [b"line1containingNewLineSymbol\nline2containingNewLineSymbol\n", b'']
        lines = self.read_using_split_stream_method(body)
        self.assertListEqual(["line1containingNewLineSymbol", "line2containingNewLineSymbol"], lines)

    def test_should_include_last_line_without_new_line_symbol(self):
        body = [b"line1containingNewLineSymbol\nline2NotContainingNewLineSymbol", b'']
        lines = self.read_using_split_stream_method(body)
        self.assertListEqual(["line1containingNewLineSymbol", "line2NotContainingNewLineSymbol"], lines)

    def test_should_work_with_weirdly_chunked_data_ending_in_new_line_symbol(self):
        body = [b"line1containin", b"gNewLineSymbol\nline2N", b"otContainingNewLineSymbol\n", b'']
        lines = self.read_using_split_stream_method(body)
        self.assertListEqual(["line1containingNewLineSymbol", "line2NotContainingNewLineSymbol"], lines)

    def test_should_work_with_weirdly_chunked_data_not_ending_in_new_line_symbol(self):
        body = [b"line1containin", b"gNewLineSymbol\nline2N", b"otContainingNewLineSymbol", b'']
        lines = self.read_using_split_stream_method(body)
        self.assertListEqual(["line1containingNewLineSymbol", "line2NotContainingNewLineSymbol"], lines)

    def test_should_work_with_two_newline_symbols(self):
        body = [b"\n\nline1\n\nline2\n\n", b'']
        lines = self.read_using_split_stream_method(body)
        self.assertTrue("line1" in lines)
        self.assertTrue("line2" in lines)

    def test_should_work_with_newline_symbols(self):
        body = [b"\nline", b'']
        lines = self.read_using_split_stream_method(body)
        self.assertTrue("line" in lines)

    @staticmethod
    def read_using_split_stream_method(chunks):
        body_mock = Mock(spec=StreamingBody)
        body_mock.read.side_effect = chunks
        not_used = 123
        return list(S3._split_stream(body_mock, not_used))
