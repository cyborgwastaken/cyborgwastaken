/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_split.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: gcyril <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/10/28 17:25:30 by gcyril            #+#    #+#             */
/*   Updated: 2019/11/13 15:53:12 by gcyril           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static	int	wordcount(char const *s, char c)
{
	int tot;
	int i;

	tot = 0;
	i = 0;
	while (s[i] != '\0')
	{
		while (s[i] != '\0' && s[i] == c)
			i++;
		if (s[i] != c && s[i] != '\0')
		{
			tot++;
			while (s[i] != c && s[i] != '\0')
				i++;
		}
	}
	return (tot);
}

static char	*newstr(char const *s, char c)
{
	unsigned int	i;
	unsigned int	j;
	char			*str;

	i = 0;
	j = 0;
	while (s[i] != '\0' && s[i] != c)
		i++;
	if (!(str = (char*)malloc(sizeof(char) * (i + 1))))
		return (NULL);
	while (s[j] != '\0' && s[j] != c)
	{
		str[j] = s[j];
		j++;
	}
	str[j] = '\0';
	return (str);
}

static char	**freeword(char **s)
{
	while (s)
	{
		free(s);
		s++;
	}
	return (NULL);
}

char		**ft_split(char const *s, char c)
{
	unsigned int	i;
	unsigned int	j;
	char			**res;

	i = 0;
	j = 0;
	if (!s)
		return (NULL);
	if (!(res = (char **)malloc(sizeof(char *) * (wordcount(s, c) + 1))))
		return (NULL);
	while (s[i] != '\0')
	{
		while (s[i] != '\0' && s[i] == c)
			i++;
		if (s[i] != '\0' && s[i] != c)
		{
			if (!(res[j] = newstr(s + i, c)))
				return (freeword(res));
			j++;
		}
		while (s[i] != '\0' && s[i] != c)
			i++;
	}
	res[j] = NULL;
	return (res);
}
