package validation

import "testing"

func TestValidateSQLiEndpoint(t *testing.T) {
	good := "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search"
	canon, err := ValidateSQLiEndpoint(good)
	if err != nil || canon != good {
		t.Fatalf("valid ingress endpoint rejected or not canonical: %q %v", canon, err)
	}
	if _, err := ValidateSQLiEndpoint("http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8001/fixture/catalog/search"); err == nil {
		t.Fatal("unapproved ingress port accepted")
	}
	for _, bad := range []string{
		"https://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search", // scheme
		good + "?category=x", // query
		good + "#frag",       // fragment
		good + "/",           // trailing slash is not the exact path
		"http://user:pw@zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search", // userinfo
		"http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/orders",                 // wrong path
		"http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog",                // short path
		"http://TRAEFIK.kube-system.svc.cluster.local/fixture/catalog/search",                            // uppercase host
		"http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000:0/fixture/catalog/search",       // bad port
		"http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000:99999/fixture/catalog/search",   // bad port
		"ftp://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search",          // scheme
		"http:///fixture/catalog/search", // empty host
		// ZR42-04: not an in-cluster ingress DNS name.
		"http://203.0.113.10/fixture/catalog/search",              // public IP literal (TEST-NET)
		"http://127.0.0.1/fixture/catalog/search",                 // loopback IP literal
		"http://10.1.2.3/fixture/catalog/search",                  // private IP literal is still not an ingress DNS name
		"http://host.local/fixture/catalog/search",                // bare host, not svc.cluster.local
		"http://traefik.svc.cluster.local/fixture/catalog/search", // missing the namespace label
		// ZR42-04: the fixture Service directly bypasses the ingress observation point.
		"http://sqli-fixture.zd-sqli-lab.svc.cluster.local/fixture/catalog/search",
	} {
		if canon, err := ValidateSQLiEndpoint(bad); err == nil {
			t.Fatalf("accepted bad endpoint %q -> %q", bad, canon)
		}
	}
}
