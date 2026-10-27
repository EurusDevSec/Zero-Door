// Package validation validates the parsed target, never a substring of a URL.
package validation

import (
	"fmt"
	"net/url"
	"strings"
)

// sqliSearchPath must match attack.SQLiSearchPath; the SQLi executor's only reachable path.
const sqliSearchPath = "/fixture/catalog/search"

// ZER-41 runtime-02 verified this dedicated private Traefik Service profile. Admission accepts no other
// service/namespace/port; the executor separately binds it to the operator-pinned Service IP.
const sqliIngressAuthority = "zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000"

// ValidateSQLiEndpoint accepts only the approved in-cluster ingress profile for the fixture search path: http,
// no credentials/query/fragment and the exact Service DNS authority/port/path. It returns the canonical base
// URL (the executor appends the single `category` query parameter it builds from the catalog). It validates both
// the configured policy endpoint and a command's target URL; admission then requires the two to be identical.
func ValidateSQLiEndpoint(raw string) (string, error) {
	u, err := url.Parse(raw)
	if err != nil || u == nil || u.Scheme != "http" || u.User != nil || u.Opaque != "" ||
		u.RawQuery != "" || u.ForceQuery || u.Fragment != "" || u.RawPath != "" ||
		strings.ContainsAny(raw, "\\%\r\n\t ?#") || strings.ToLower(raw) != raw ||
		u.Host != sqliIngressAuthority || u.Path != sqliSearchPath {
		return "", fmt.Errorf("SQLI_ENDPOINT")
	}
	return u.String(), nil
}

type Target struct {
	Namespace string `json:"namespace"`
	Service   string `json:"service"`
	URL       string `json:"url"`
}

type Validator struct {
	targets    []Target
	namespaces map[string]bool
}

func New(namespaces []string) *Validator {
	targets := []Target{}
	for _, service := range []string{"frontend", "cartservice", "productcatalogservice", "currencyservice", "checkoutservice", "redis-cart", "shippingservice", "paymentservice", "emailservice"} {
		target := Target{Namespace: "target-app", Service: service}
		if service == "frontend" {
			target.URL = "http://frontend.target-app.svc.cluster.local/"
		}
		targets = append(targets, target)
	}
	return NewWithTargets(namespaces, targets)
}

func NewWithTargets(namespaces []string, targets []Target) *Validator {
	v := &Validator{targets: targets, namespaces: map[string]bool{}}
	for _, n := range namespaces {
		if n == "target-app" {
			v.namespaces[n] = true
		}
	}
	return v
}

func (v *Validator) ValidateNamespace(namespace string) error {
	if !v.namespaces[namespace] {
		return fmt.Errorf("TARGET_NAMESPACE")
	}
	return nil
}

func parsed(raw string) (*url.URL, error) {
	u, err := url.Parse(raw)
	if err != nil || u == nil || u.Scheme != "http" || u.User != nil || u.Opaque != "" ||
		u.RawQuery != "" || u.ForceQuery || u.Fragment != "" || u.RawPath != "" ||
		strings.ContainsAny(raw, "\\%\r\n\t ") || u.Hostname() != "frontend.target-app.svc.cluster.local" ||
		(u.Host != "frontend.target-app.svc.cluster.local" && u.Host != "frontend.target-app.svc.cluster.local:80") ||
		(u.Port() != "" && u.Port() != "80") || (u.Path != "" && u.Path != "/") {
		return nil, fmt.Errorf("TARGET_URL")
	}
	if u.Path == "" {
		u.Path = "/"
	}
	// An explicit default port is equivalent; no other port is accepted.
	u.Host = u.Hostname()
	return u, nil
}

func (v *Validator) ValidateURL(raw string) error {
	u, err := parsed(raw)
	if err != nil {
		return err
	}
	for _, t := range v.targets {
		if !v.namespaces[t.Namespace] || t.URL == "" {
			continue
		}
		allowed, e := parsed(t.URL)
		if e == nil && u.String() == allowed.String() {
			return nil
		}
	}
	return fmt.Errorf("TARGET_URL_NOT_ALLOWED")
}

// Resolve validates the service and the URL actually used, including a derived URL.
func (v *Validator) Resolve(namespace, service, raw string, httpTarget bool) (string, error) {
	if err := v.ValidateNamespace(namespace); err != nil {
		return "", err
	}
	for _, t := range v.targets {
		if t.Namespace != namespace || t.Service != service {
			continue
		}
		if !httpTarget {
			if raw != "" {
				return "", fmt.Errorf("UNEXPECTED_URL")
			}
			return "", nil
		}
		if raw == "" {
			raw = fmt.Sprintf("http://%s.%s.svc.cluster.local/", service, namespace)
		}
		if t.URL == "" {
			return "", fmt.Errorf("TARGET_ROUTE")
		}
		u, err := parsed(raw)
		if err != nil {
			return "", err
		}
		allowed, err := parsed(t.URL)
		if err != nil || allowed.String() != u.String() {
			return "", fmt.Errorf("TARGET_ROUTE")
		}
		return u.String(), nil
	}
	return "", fmt.Errorf("TARGET_SERVICE")
}
