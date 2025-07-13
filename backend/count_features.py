from feature_extraction import AudioPreprocessor

processor = AudioPreprocessor()
feature_names = processor.get_feature_names()

print("FEATURE COUNT BREAKDOWN:")
print("=" * 50)

# Count each category
mfcc_count = sum(1 for f in feature_names if f.startswith('mfcc_'))
delta_count = sum(1 for f in feature_names if f.startswith('delta_mfcc_'))
delta2_count = sum(1 for f in feature_names if f.startswith('delta2_mfcc_'))
chroma_count = sum(1 for f in feature_names if f.startswith('chroma_'))
contrast_count = sum(1 for f in feature_names if f.startswith('contrast_'))
other_count = len(feature_names) - mfcc_count - delta_count - delta2_count - chroma_count - contrast_count

print(f"MFCC features: {mfcc_count}")
print(f"Delta MFCC features: {delta_count}")
print(f"Delta² MFCC features: {delta2_count}")
print(f"Chroma features: {chroma_count}")
print(f"Spectral Contrast features: {contrast_count}")
print(f"Other features: {other_count}")
print("-" * 30)
print(f"TOTAL: {len(feature_names)} features")
print()

if len(feature_names) == 60:
    print("🎯 PERFECT! 60 features")
elif len(feature_names) > 60:
    excess = len(feature_names) - 60
    print(f"❌ TOO MANY: {excess} extra features")
else:
    shortage = 60 - len(feature_names)
    print(f"❌ TOO FEW: {shortage} missing features")

print("\nFirst 10 feature names:")
for i, name in enumerate(feature_names[:10]):
    print(f"  {i+1}. {name}")
    
print("\nLast 10 feature names:")
for i, name in enumerate(feature_names[-10:], len(feature_names)-9):
    print(f"  {i}. {name}")
