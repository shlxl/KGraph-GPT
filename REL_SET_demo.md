{
  "name": "GraphRAG-RELSET-GenericWeb-zh",
  "version": "2025-11-08",
  "types": [
    "Person",
    "Organization",
    "Project",
    "Product",
    "Work",
    "Event",
    "Location",
    "Regulation",
    "Value"
  ],
  "relations": [
    { "name": "partner_with", "domain": ["Organization","Person"], "range": ["Organization","Person"], "symmetric": true },
    { "name": "member_of", "domain": ["Person","Organization"], "range": ["Organization"], "symmetric": false },
    { "name": "sub_organization_of", "domain": ["Organization"], "range": ["Organization"], "inverse": "has_sub_organization", "maps_to": "schema.org/subOrganization" },
    { "name": "has_sub_organization", "domain": ["Organization"], "range": ["Organization"], "inverse": "sub_organization_of", "maps_to": "schema.org/parentOrganization" },
    { "name": "affiliated_with", "domain": ["Person","Organization"], "range": ["Organization","Person"], "symmetric": true },
    { "name": "owns", "domain": ["Organization","Person"], "range": ["Organization","Product","Work","Project"], "symmetric": false },
    { "name": "acquired", "domain": ["Organization"], "range": ["Organization","Product"], "symmetric": false },
    { "name": "invests_in", "domain": ["Organization","Person"], "range": ["Organization","Project","Product"], "symmetric": false },
    { "name": "funds", "domain": ["Organization","Person"], "range": ["Project","Event","Organization","Work"], "symmetric": false },
    { "name": "adds_funding", "domain": ["Organization","Person"], "range": ["Project","Event","Organization","Work"], "symmetric": false },
    { "name": "leads", "domain": ["Person","Organization"], "range": ["Project","Organization","Event"], "symmetric": false },
    { "name": "manages", "domain": ["Person","Organization"], "range": ["Project","Organization","Event"], "symmetric": false },
    { "name": "holds_role", "domain": ["Person"], "range": ["Organization","Project","Event"], "symmetric": false },
    { "name": "held_role", "domain": ["Person"], "range": ["Organization","Project","Event"], "symmetric": false },
    { "name": "joins", "domain": ["Person","Organization"], "range": ["Organization","Project"], "symmetric": false },
    { "name": "located_in", "domain": ["Organization","Project","Event","Product","Work","Location"], "range": ["Location"], "symmetric": false },
    { "name": "part_of", "domain": ["Location","Project","Organization","Work","Event"], "range": ["Location","Project","Organization","Work","Event"], "symmetric": false },
    { "name": "nearby", "domain": ["Location","Project","Event"], "range": ["Location"], "symmetric": true },
    { "name": "releases", "domain": ["Organization","Person"], "range": ["Product","Work"], "symmetric": false },
    { "name": "publishes", "domain": ["Organization","Person"], "range": ["Work"], "symmetric": false },
    { "name": "announces", "domain": ["Organization","Person"], "range": ["Project","Product","Event","Work"], "symmetric": false },
    { "name": "wins_award", "domain": ["Organization","Person","Work"], "range": ["Value"], "symmetric": false },
    { "name": "alias_of", "domain": ["*"], "range": ["*"], "symmetric": true },
    { "name": "not_same_as", "domain": ["*"], "range": ["*"], "symmetric": true },
    { "name": "denies", "domain": ["Organization","Person"], "range": ["Event","Project","Claim","Value"], "symmetric": false },
    { "name": "rumor_about", "domain": ["Event","Value","Claim"], "range": ["Project","Organization","Person"], "symmetric": false },
    { "name": "caused", "domain": ["Organization","Person","Event"], "range": ["Event"], "symmetric": false },
    { "name": "caused_by", "domain": ["Event"], "range": ["Organization","Person","Event"], "symmetric": false }
  ],
  "negation_prefix": "negated:",
  "qualifiers": {
    "since": "YYYY-MM[-DD]",
    "until": "YYYY-MM[-DD]",
    "date": "YYYY-MM[-DD]",
    "amount": "string (数值+单位，如 3.2亿元 / 25 million USD)",
    "currency": "ISO-4217，可选；若 amount 已含货币可忽略",
    "pct": "number (0-100)",
    "count": "integer",
    "distance_km": "number",
    "duration_iso8601": "PnYnMnDTnHnM",
    "role": "string",
    "place_role": "enum[hq, registered, event_site, manufacture_site]",
    "alias": "string",
    "direction": "string",
    "gw": "number",
    "mw": "number",
    "turbines": "integer",
    "note": "string"
  },
  "evidence_schema": {
    "doc": "<DOC_ID>",
    "sents": [1,2]
  },
  "output": {
    "format": "JSONL",
    "example": [
      {
        "head": {"text":"示例科技集团","type":"Organization"},
        "relation": "sub_organization_of",
        "tail": {"text":"示例控股","type":"Organization"},
        "qualifiers": {},
        "evidence": [{"doc":"dX","sents":[3]}],
        "confidence": 0.84
      },
      {
        "head": {"text":"张三","type":"Person"},
        "relation": "holds_role",
        "tail": {"text":"示例科技集团","type":"Organization"},
        "qualifiers": {"role":"首席执行官","since":"2024-05"},
        "evidence": [{"doc":"dY","sents":[5]}],
        "confidence": 0.82
      },
      {
        "head": {"text":"示例科技集团","type":"Organization"},
        "relation": "funds",
        "tail": {"text":"Alpha 项目","type":"Project"},
        "qualifiers": {"amount":"2亿元","date":"2025-01-10"},
        "evidence": [{"doc":"dZ","sents":[2]}],
        "confidence": 0.83
      },
      {
        "head": {"text":"市监管局","type":"Organization"},
        "relation": "denies",
        "tail": {"text":"event.示例数据泄露.2025-02-01","type":"Event"},
        "qualifiers": {"date":"2025-02-02"},
        "evidence": [{"doc":"dN","sents":[7,8]}],
        "confidence": 0.81
      },
      {
        "head": {"text":"event.示例服务中断.2025-03-20","type":"Event"},
        "relation": "negated:caused_by",
        "tail": {"text":"Alpha 项目","type":"Project"},
        "qualifiers": {"note":"官方通报排除直接关联"},
        "evidence": [{"doc":"dM","sents":[4]}],
        "confidence": 0.80
      }
    ]
  },
  "policies": {
    "evidence_min_unit": "sentence",
    "allow_multi_sentence_evidence": true,
    "drop_facts_without_verifiable_evidence": true,
    "use_alias_of_for_synonyms_only": true,
    "use_not_same_as_for_name_collision": true,
    "negation_as_prefix_only": true
  },
  "authority_order_for_disputes": [
    "GovernmentAgency",
    "Regulator",
    "Court",
    "Government",
    "InternationalOrg",
    "CompanyOfficial",
    "ResearchOrg",
    "MajorNews",
    "LocalNews",
    "SocialMedia"
  ]
}
