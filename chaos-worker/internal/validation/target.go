// Package validation provides blast-radius safety controls for the Chaos Worker.
// All attack targets MUST pass validation before any destructive action is taken.
package validation

import (
	"fmt"
	"log/slog"
	"strings"
)

// Validator enforces blast-radius constraints.
type Validator struct {
	allowedNamespaces map[string]struct{}
	allowedDNSSuffix  string
}

// New creates a Validator with the given whitelist of Kubernetes namespaces.
func New(allowedNamespaces []string) *Validator {
	ns := make(map[string]struct{}, len(allowedNamespaces))
	for _, n := range allowedNamespaces {
		ns[strings.TrimSpace(n)] = struct{}{}
	}
	return &Validator{
		allowedNamespaces: ns,
		allowedDNSSuffix:  ".target-app.svc.cluster.local",
	}
}

// ValidateNamespace returns nil if the namespace is whitelisted, otherwise an error.
func (v *Validator) ValidateNamespace(namespace string) error {
	if _, ok := v.allowedNamespaces[namespace]; !ok {
		slog.Error("BLAST RADIUS VIOLATION — namespace not in whitelist",
			"requested_namespace", namespace,
			"allowed_namespaces", v.allowedNamespaces,
			"severity", "CRITICAL",
		)
		return fmt.Errorf("REJECTED: namespace '%s' is not in the allowed list %v — blast radius violation", namespace, v.allowedNamespaces)
	}
	return nil
}

// ValidateURL returns nil if the URL's host matches the allowed DNS pattern.
// It prevents attacks from being directed outside the cluster or to system namespaces.
func (v *Validator) ValidateURL(rawURL string) error {
	if rawURL == "" {
		return nil // URL not required for all attack types
	}
	lower := strings.ToLower(rawURL)

	// Must match the allowed cluster-internal DNS suffix
	if !strings.Contains(lower, v.allowedDNSSuffix) {
		slog.Error("BLAST RADIUS VIOLATION — target URL does not match allowed DNS pattern",
			"requested_url", rawURL,
			"required_suffix", v.allowedDNSSuffix,
			"severity", "CRITICAL",
		)
		return fmt.Errorf("REJECTED: target URL '%s' does not match allowed pattern '*%s' — blast radius violation", rawURL, v.allowedDNSSuffix)
	}

	// Must not target system namespaces even if suffix matches (defence in depth)
	blockedPrefixes := []string{"kube-system", "monitoring", "zero-door"}
	for _, blocked := range blockedPrefixes {
		if strings.Contains(lower, blocked) {
			slog.Error("BLAST RADIUS VIOLATION — target URL contains blocked namespace",
				"requested_url", rawURL,
				"blocked_namespace", blocked,
				"severity", "CRITICAL",
			)
			return fmt.Errorf("REJECTED: target URL '%s' targets blocked namespace '%s' — blast radius violation", rawURL, blocked)
		}
	}

	return nil
}
