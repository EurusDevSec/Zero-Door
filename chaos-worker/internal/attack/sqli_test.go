package attack

import (
	"encoding/json"
	"os"
	"strings"
	"testing"
)

// The locked disclosure template must stay byte-identical to the pattern ZER-41 already reviewed; the catalog
// must carry exactly one injection entry and no destructive/DDL tokens at all.
func TestSQLiCatalogMatchesZER41OracleAndStaysMinimal(t *testing.T) {
	raw, err := os.ReadFile("../../../tests/fixtures/zer41/expected.json")
	if err != nil {
		t.Fatal(err)
	}
	var exp struct {
		Injection struct {
			Category string `json:"category"`
		} `json:"injection"`
	}
	if err := json.Unmarshal(raw, &exp); err != nil {
		t.Fatal(err)
	}
	tmpl, ok := LookupSQLiTemplate("disclose-restricted")
	if !ok {
		t.Fatal("disclosure template missing from catalog")
	}
	if tmpl.Category != exp.Injection.Category {
		t.Fatalf("catalog drift: catalog=%q expected.json=%q", tmpl.Category, exp.Injection.Category)
	}
	if tmpl.Kind != "injection" {
		t.Fatalf("disclosure template kind = %q, want injection", tmpl.Kind)
	}

	injections := 0
	for _, id := range SQLiTemplateIDs() {
		e, ok := LookupSQLiTemplate(id)
		if !ok || e.ID != id {
			t.Fatalf("id lookup mismatch for %q", id)
		}
		if e.Kind != "injection" && e.Kind != "benign" {
			t.Fatalf("entry %q has unexpected kind %q", id, e.Kind)
		}
		if e.Kind == "injection" {
			injections++
		}
		upper := strings.ToUpper(e.Category)
		for _, token := range []string{"DELETE", "DROP", "INSERT", "UPDATE", "UNION", ";"} {
			if strings.Contains(upper, token) {
				t.Fatalf("catalog entry %q contains forbidden token %q: %q", id, token, e.Category)
			}
		}
	}
	if injections != 1 {
		t.Fatalf("catalog has %d injection templates, want exactly 1", injections)
	}

	// Cross-language anti-drift: the catalog ids must equal the canonical list the Python suite also checks.
	canon, err := os.ReadFile("../../../tests/fixtures/zer42/catalog-ids.json")
	if err != nil {
		t.Fatal(err)
	}
	var ids struct {
		InjectionID string   `json:"injection_id"`
		TemplateIDs []string `json:"template_ids"`
	}
	if err := json.Unmarshal(canon, &ids); err != nil {
		t.Fatal(err)
	}
	if ids.InjectionID != "disclose-restricted" {
		t.Fatalf("canonical injection id drift: %q", ids.InjectionID)
	}
	got := strings.Join(SQLiTemplateIDs(), ",")
	want := strings.Join(ids.TemplateIDs, ",") // catalog-ids.json lists them sorted
	if got != want {
		t.Fatalf("catalog id drift: go=%q canonical=%q", got, want)
	}
}

func TestSQLiCeilingsAreTheDesignLimits(t *testing.T) {
	if SQLiConcurrency != 1 || SQLiMaxRPS != 1 || SQLiMaxSends != 20 || SQLiPerCommandSec != 30 || SQLiMaxResponse != 256*1024 || SQLiRequestMs != 3000 {
		t.Fatalf("design ceilings drifted: %d %d %d %d %d %d", SQLiConcurrency, SQLiMaxRPS, SQLiMaxSends, SQLiPerCommandSec, SQLiMaxResponse, SQLiRequestMs)
	}
	if SQLiSearchPath != "/fixture/catalog/search" || SQLiNamespace != "zd-sqli-lab" || SQLiService != "sqli-fixture" {
		t.Fatal("locked identifiers drifted")
	}
}
