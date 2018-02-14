import re

text="""
Comment Maître Cerise, le menuisier, trouva un morceau de
bois qui pleurait et riait comme un enfant.
Il était une fois…
– Un roi ! – vont dire mes petits lecteurs.
Eh bien non, les enfants, vous vous trompez. Il était une fois…
un morceau de bois.
Ce n’était pas du bois précieux, mais une simple bûche, de
celles qu’en hiver on jette dans les poêles et dans les cheminées.
Je ne pourrais pas expliquer comment, mais le fait est qu’un
beau jour ce bout de bois se retrouva dans l’atelier d’un vieux
menuisier, lequel avait pour nom Antonio bien que tout le monde
l’appelât Maître Cerise à cause de la pointe de son nez qui était
toujours brillante et rouge foncé, comme une cerise mûre.
Apercevant ce morceau de bois, Maître Cerise devint tout
joyeux et, se frottant les mains, marmonna :
– Ce rondin est arrivé à point : je vais m’en servir pour
fabriquer un pied de table.
Sitôt dit, sitôt fait : pour enlever l’écorce et le dégrossir, il
empoigna sa hache bien aiguisée. Mais comme il allait donner le
premier coup, son bras resta suspendu en l’air car il venait
d’entendre une toute petite voix qui le suppliait :fants, vous vous trompez. Il était une fois…
un morceau de bois."""

sliced = re.split(r"\n", text)
print(sliced)
reformatted = ""
for line in sliced:
	if not line:
		pass
	elif line[-1] in {".", "?", ":", "!", ";", "…"}:
		reformatted+=("\n"+line)
	else:
		print(line[-1])
		reformatted+=(" "+line)

print(reformatted)