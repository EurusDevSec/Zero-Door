package baseline_test
import (
 "testing"
 "time"
 "baseline/attack"
 "baseline/validation"
)
func TestURLConfusionRejected(t *testing.T){if err:=validation.New([]string{"target-app"}).ValidateURL("http://outside.invalid/.target-app.svc.cluster.local");err==nil{t.Fatal("outside URL accepted")}}
func TestOperatorDurationCap(t *testing.T){c:=attack.AttackCommand{Parameters:attack.AttackParameters{DurationSec:3600},SafetyLimits:attack.SafetyLimits{MaxDurationSec:3600}};if got:=attack.EffectiveDuration(c,1);got!=time.Second{t.Fatal("operator cap exceeded",got)}}
func TestDuplicateJSONRejected(t *testing.T){if _,err:=attack.ParseCommand([]byte(`{"commandId":"a","commandId":"b"}`));err==nil{t.Fatal("duplicate key accepted")}}
func TestValidControl(t *testing.T){if err:=validation.New([]string{"target-app"}).ValidateURL("http://frontend.target-app.svc.cluster.local/");err!=nil{t.Fatal(err)};c:=attack.AttackCommand{Parameters:attack.AttackParameters{DurationSec:1},SafetyLimits:attack.SafetyLimits{MaxDurationSec:1}};if got:=attack.EffectiveDuration(c,1);got!=time.Second{t.Fatal(got)}}
