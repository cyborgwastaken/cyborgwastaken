/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strtrim.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: gcyril <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/10/26 14:28:58 by gcyril            #+#    #+#             */
/*   Updated: 2019/11/06 15:43:06 by gcyril           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static int	matchset(char const c, char const *set)
{
	while (*set)
	{
		if (*set == c)
			return (1);
		set++;
	}
	return (0);
}

char		*ft_strtrim(char const *s1, char const *set)
{
	int		size;
	char	*s2;

	if (!s1 || !set)
		return (NULL);
	while (s1 && matchset(*s1, set))
		s1++;
	size = ft_strlen(s1) - 1;
	while (size > 0 && matchset(s1[size], set))
		size--;
	if (s1 == '\0')
		return (ft_calloc(1, sizeof(char)));
	s2 = ft_substr(s1, 0, size + 1);
	return (s2);
}
