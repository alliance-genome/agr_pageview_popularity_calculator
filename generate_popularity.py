import pandas as pd

# multiplier used on page views for orthologs
scale_factor = .1

alliance = pd.read_csv('alliance_urls.txt', sep='\t', names=['id', 'alliance_count'])
flybase = pd.read_csv('flybase_urls.txt', sep='\t', names=['id', 'mod_count'])
mgi = pd.read_csv('mgi_urls.txt', sep='\t', names=['id', 'mod_count'])
zfin = pd.read_csv('zfin_urls.txt', sep='\t', names=['id', 'mod_count'])
orthology = pd.read_csv('ORTHOLOGY-ALLIANCE_COMBINED_37.tsv', sep='\t', comment='#')

id_capture = r'\/([^/]+)$'
alliance['id'] = alliance['id'].str.extract(id_capture)
flybase['id'] = flybase['id'].str.extract(id_capture)
mgi['id'] = mgi['id'].str.extract(id_capture)
zfin['id'] = zfin['id'].str.extract(id_capture)
# convert local IDs to curies
flybase['id'] = flybase['id'].apply(lambda x: x if ':' in x else 'FB:' + x)
zfin['id'] = zfin['id'].apply(lambda x: x if ':' in x else 'ZFIN:' + x)

alliance.set_index('id', inplace=True)
flybase.set_index('id', inplace=True)
mgi.set_index('id', inplace=True)
zfin.set_index('id', inplace=True)

# write simple popularity files
alliance.to_csv('alliance_popularity.tsv', sep='\t', header=None)
flybase.to_csv('flybase_populiarty.tsv', sep='\t', header=None)
mgi.to_csv('mgi_populiarty.tsv', sep='\t', header=None)
zfin.to_csv('zfin_populiarty.tsv', sep='\t', header=None)

# keep only best score matches, slim down to just the two gene IDs
orthology = orthology[orthology.IsBestScore == 'Yes']
orthology = orthology[orthology.Gene1SpeciesName == 'Homo sapiens']
orthology = orthology[['Gene1ID', 'Gene2ID']]

# now generate the enhanced popularity file, with a lil something extra for human genes
all_mods = pd.concat([flybase, mgi, zfin])

orthopop = orthology.merge(all_mods, how='left', left_on='Gene2ID', right_index=True)
orthopop = orthopop.rename(columns={'mod_count': 'Gene2ModCount'})

orthopop = orthopop.merge(alliance, how='left', left_on='Gene2ID', right_index=True)
orthopop = orthopop.rename(columns={'alliance_count': 'Gene2AllianceCount'})

orthopop = orthopop.merge(alliance, how='left', left_on='Gene1ID', right_index=True)
orthopop = orthopop.rename(columns={'alliance_count': 'Gene1AllianceCount'})

orthopop['Gene2ModCount'] = orthopop['Gene2ModCount'].fillna(0)
orthopop['Gene2AllianceCount'] = orthopop['Gene2AllianceCount'].fillna(0)
orthopop['Gene1AllianceCount'] = orthopop['Gene1AllianceCount'].fillna(0)

orthopop = orthopop.assign(Gene2ModCountScaled=lambda row: row.Gene2ModCount * scale_factor)
orthopop = orthopop.assign(Gene2AllianceCountScaled=lambda row: row.Gene2AllianceCount * scale_factor)

orthopop['computed'] = orthopop[['Gene2ModCountScaled', 'Gene2AllianceCountScaled']].sum(axis=1)

totalpop = orthopop[['Gene1ID', 'computed']].groupby(['Gene1ID']).sum()

alliance = alliance.join(totalpop, how='left')
alliance['computed'] = alliance['computed'].fillna(0)
alliance = alliance.assign(popularity=alliance['alliance_count'] + alliance['computed'])

popularity = alliance['popularity']

# Duplicates can happen, like a request for '/gene/DOID:123456' because people do weird things
# just sum them to safely deduplicate (dropping lower value might be safer for weeding out?)
popularity = popularity.groupby(level=0).sum()

popularity.to_csv('enhanced-alliance-popularity.tsv', sep='\t', header=None)
