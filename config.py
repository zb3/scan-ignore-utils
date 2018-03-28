#NOTE: these ranges are passed to re.compile

gov_misc = ['USAISC', 'DoD', r'\bNASA', 'National Aeronautics', '754th', 'Navy Network Information Center', 'DARPA', r'\bUSDA', '^State of ', '(?i)department', '(?i)agency', 'Shared Services Canada']

uni_edu = ['(?i)university', '(?i)research', '(?i)academ(y|ic)', '(?i)institute', '(?i)education', '(?i)universidad', '(?i)science', '(?i)scientific', r'(?i)college\b']

nerns = ['WiscNet', 'BELNET', 'CESNET', 'UNINETT', 'SURFnet', '^ARNES$', 'Consortium GARR|Cineca Consorzio',
         'Renater',  'ACONET', 'Tieteen tietotekniikan', '^SUNET ', 'Jisc Services Limited', 'Fundacao para a Ciencia',
         'Entidad Publica Empresarial Red.es', '^BCnet', 'AARNet', 'National Center for High-performance Computing',
         'Deutschen Forschungsnetzes', '^ESnet', 'HEAnet', 'Merit Network', 'Rede Nacional de Ensino e Pesquisa',
         '[(]RISQ', 'RESTENA', 'Zdruzenie pouzivatelov Slovenskej akademickej', '^SWITCH$']

#CDNs, nothing interesting there
cdns = ['Cloudflare', 'Incapsula', 'Akamai', 'Fastly', 'Content Delivery Network Ltd']

#some  hosting providers (kinda), websites + some classic dbs here but not devices. note "EGIHosting" doesn't like being scanned
hosting = ['(?i)host', 'Enzu Inc', 'GoDaddy.com', 'PEG TECH INC', 'Strato AG', '(?i)unified layer', '(?i)1&1 internet']

#largest ones,
cloud_providers = ['Digital ?Ocean', 'Google (LLC|Ireland|Switz)', 'Amazon([.]com| Data Services)', '(?i)rackspace',
                    'Microsoft', 'OVH SAS', 'SoftLayer Technologies', 'Linode, LLC', '(?i)hetzner', 'Hangzhou Alibaba Advertising']



####
#### ignore_patterns is only for ignore-ranges.py
####

#by default we ignore all of the ranges above as originally this was for devices only

ignore_misc = ['^HT$']

ignore_patterns = gov_misc + uni_edu + nerns + cdns + hosting + cloud_providers + ignore_misc

#groups are optional, for statistics only
ignore_pattern_groups = [['gov + defense', gov_misc], ['universities', uni_edu], ['NERN', nerns], ['CDN', cdns], ['hosting', hosting], ['cloud', cloud_providers]]

####
#### include_patterns is only for include-ranges.py
####

include_patterns = cloud_providers
include_pattern_groups = [['cloud', cloud_providers]]
