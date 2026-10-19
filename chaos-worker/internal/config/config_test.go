package config

import "testing"

func TestInvalidConfigDoesNotFallBackToPermissiveDefaults(t *testing.T) {
	for _, key := range []string{"MAX_ATTACK_DURATION_SEC", "DEFAULT_CONCURRENCY", "DEFAULT_RPS"} {
		for _, value := range []string{"garbage", "-1", "0", "9999999999999999999999999999999"} {
			t.Run(key+value, func(t *testing.T) {
				t.Setenv(key, value)
				if Load().Error == nil {
					t.Fatal("invalid config accepted")
				}
			})
		}
	}
}
