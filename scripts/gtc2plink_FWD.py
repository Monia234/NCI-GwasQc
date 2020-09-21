import sys
import os
from IlluminaBeadArrayFiles import GenotypeCalls, BeadPoolManifest, code2genotype






def getCR(GenoScores, genoThresh = 0.25):
    '''
    GenoScores = gtc.get_genotype_scores()
    '''
    c = 0
    for g in GenoScores:
        if g < genoThresh:
            c += 1
    return float(len(GenoScores) - c)/len(GenoScores)


##It looks like the no call cutoff defaults to genotype_score of .15.  I'll change it to 0.25 using the code above in getCR
def outputPlink(gtc_file, manifest_file, sample_name, plink_out_dir, genoThresh = 0.15):
    manifest = BeadPoolManifest(manifest_file)
    gtc = GenotypeCalls(gtc_file)
    GenoScores = gtc.get_genotype_scores()
    forward_strand_genotypes = gtc.get_base_calls_forward_strand(manifest.snps, manifest.source_strands)
    outBase = plink_out_dir + '/' + sample_name
    allGenotypes = []
    with open(outBase + '.ped', 'w') as pedOut, open(outBase +'.map','w') as mapOut:
        for (name, chrom, map_info, source_strand_genotype, genoScore) in zip(manifest.names, manifest.chroms, manifest.map_infos, forward_strand_genotypes, GenoScores):
            mapOut.write(' '.join([chrom, name, '0', str(map_info)]) + '\n')
            if source_strand_genotype == '-':
                geno = ['0', '0']
            else:
                geno = [source_strand_genotype[0], source_strand_genotype[1]]
            allGenotypes += geno
        pedOut.write(' '.join([sample_name, sample_name, '0', '0', '0', '-9'] + allGenotypes) + '\n')


def main():
    args = sys.argv[1:]
    if len(args) != 4:
        print ("error: usage: python gtc2plink.py /path/to/file.gtc /path/to/manifest.bpm sample_name /path/to/out/dir")
        sys.exit(1)
    else:
        outputPlink(args[0], args[1], args[2], args[3])


if __name__ == "__main__":
    main()
