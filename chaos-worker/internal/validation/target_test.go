package validation

import "testing"

func TestExactTargetAndDerivedURL(t *testing.T) {
	v := New([]string{"target-app", "monitoring"})
	for _, raw := range []string{"", "http://frontend.target-app.svc.cluster.local", "http://frontend.target-app.svc.cluster.local:80/"} {
		got, err := v.Resolve("target-app", "frontend", raw, true)
		if err != nil || got != "http://frontend.target-app.svc.cluster.local/" {
			t.Fatal(got, err)
		}
	}
	for _, raw := range []string{
		"http://outside.invalid/.target-app.svc.cluster.local", "http://frontend.target-app.svc.cluster.local.outside.invalid/",
		"http://frontend.target-app.svc.cluster.local@outside.invalid/", "https://frontend.target-app.svc.cluster.local/",
		"http://frontend.target-app.svc.cluster.local:8080/", "http://frontend.target-app.svc.cluster.local:/",
		"http://frontend.target-app.svc.cluster.local/%2f", "http://frontend.target-app.svc.cluster.local/?next=http://outside.invalid",
		"http://127.0.0.1/", "http://[::1]/", "http://frontend.target-app.svc.cluster.local/admin", "http://frontend.target-app.svc.cluster.local/#x",
		"http://frontend.target-app.svc.cluster.local/?", "http://frontend.target-app.svc.cluster.local\\@outside.invalid/",
	} {
		if _, err := v.Resolve("target-app", "frontend", raw, true); err == nil {
			t.Fatal("URL admitted", raw)
		}
	}
	for _, target := range []Target{{"monitoring", "frontend", ""}, {"target-app", "frontend,other", ""}, {"target-app", "cartservice", ""}} {
		if _, err := v.Resolve(target.Namespace, target.Service, target.URL, true); err == nil {
			t.Fatal(target)
		}
	}
	if _, err := v.Resolve("target-app", "cartservice", "", false); err != nil {
		t.Fatal(err)
	}
}
