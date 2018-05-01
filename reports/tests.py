from django.test import TestCase

from .report_builder import query_parser


class ProperlyParseQueriesToPrimitives(TestCase):

    def test_query_values_parsed_properly(self):
        query_string = "boolean=t&boolean2=false&int1=2" +\
            "&string=dog&intlist=1,2,3,5&list2=10&list2=cat"

        parsed = query_parser(query_string)
        print("Parsed:\n", parsed)

        self.assertEqual(parsed["boolean"], True)
        self.assertEqual(parsed["boolean2"], False)
        self.assertEqual(parsed["int1"], 2)
        self.assertEqual(parsed["string"], "dog")
        self.assertEqual(parsed["intlist"], [1, 2, 3, 5])
        self.assertEqual(parsed["list2"], [10, "cat"])

