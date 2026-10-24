import unittest

from growth.models import Institution, Fact, Source, ResearchRequest
from growth.evidence import ground_fact, confirm_competitors


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.bank = Institution(name="Example Bank", domain="example.com")
        self.source = Source(id="s1", title="Checking", url="https://www.example.com/checking", excerpt="Monthly fee is $12 or $0 with qualifying direct deposit.", retrieved_at="2026-10-24T12:00:00Z")

    def test_claim_requires_matching_source_and_quote(self):
        fact = ground_fact(Fact(value="$12 or $0 with qualifying direct deposit", source_id="s1", quote=self.source.excerpt), [self.source], self.bank)
        self.assertEqual(fact.status, "Source-supported")
        for bad in [Fact(value="$12", source_id="invented", quote="Monthly fee is $12"), Fact(value="$99", source_id="s1", quote=self.source.excerpt), Fact(value="$12", source_id="s1", quote="Invented quote $12")]:
            self.assertEqual(ground_fact(bad, [self.source], self.bank).value, "Not verified")

    def test_third_party_and_lookalike_sources_are_not_official(self):
        for url in ["https://example.com.attacker.org/checking", "https://blog.example.net/checking"]:
            source = self.source.model_copy(update={"url": url})
            self.assertEqual(ground_fact(Fact(value="$12", source_id="s1", quote=source.excerpt), [source], self.bank).status, "Not verified")

    def test_empty_quote_and_unknown_are_not_zero(self):
        self.assertEqual(ground_fact(Fact(value="$0", source_id="s1", quote=""), [self.source], self.bank).value, "Not verified")
        self.assertEqual(Fact().value, "Not verified")

    def test_competitors_must_be_three_distinct_institutions(self):
        competitors = [Institution(name=x, domain=f"{x}.com") for x in ["one", "two", "three"]]
        self.assertEqual(len(confirm_competitors(self.bank, competitors)), 3)
        for invalid in [competitors[:2], [self.bank, *competitors[:2]], [competitors[0]] * 3]:
            with self.assertRaises(ValueError):
                confirm_competitors(self.bank, invalid)

    def test_domains_are_normalized_and_private_hosts_rejected(self):
        self.assertEqual(Institution(name="Test", domain="https://www.example.com/path").domain, "example.com")
        for domain in ["localhost", "127.0.0.1", "10.0.0.1", "https://user:pass@example.com", "example.com:1234"]:
            with self.assertRaises(ValueError):
                Institution(name="Bad", domain=domain)

    def test_request_rejects_blank_market(self):
        with self.assertRaises(ValueError):
            ResearchRequest(home=self.bank, market=" ")


if __name__ == "__main__":
    unittest.main()
